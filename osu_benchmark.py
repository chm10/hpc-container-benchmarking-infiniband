import hpccm

hpccm.config.set_container_format('singularity')
hpccm.config.set_singularity_version('3.8')

Stage0 = hpccm.Stage()
Stage1 = hpccm.Stage()

# ==========================================
# ESTÁGIO 0: BUILD (Desenvolvimento)
# ==========================================
Stage0 += hpccm.primitives.baseimage(image='ubuntu:24.04', _as='devel')
Stage0 += hpccm.primitives.shell(commands=['set -e'])

Stage0 += hpccm.building_blocks.packages(ospackages=[
    'build-essential', 'wget', 'git', 'python3', 'ca-certificates',
    'file', 'pkg-config', 'automake', 'autoconf', 'libtool', 'm4',
    'bison', 'flex', 'libnuma-dev', 'libhwloc-dev', 'libxml2-dev',
    'libpciaccess-dev', 'zlib1g-dev', 'libibverbs-dev', 'librdmacm-dev',
    'ibverbs-providers', 'binutils-dev', 'libzstd-dev'
])

Stage0 += hpccm.building_blocks.gnu()

# UCX 1.22.0 com suporte a mlx5_dv
Stage0 += hpccm.building_blocks.ucx(
    version='1.22.0',
    cuda=False,
    verbs=True,
    rdmacm=True,
    disable_static=True,
    enable_mt=False,
    prefix='/usr/local/ucx',
    configure_opts=[
        '--disable-compiler-warnings',
        '--with-rdmacm',
        '--with-verbs',
        '--with-mlx5-dv'
    ]
)

# MPICH 5.0.2 CH4:UCX
Stage0 += hpccm.building_blocks.mpich(
    version='5.0.2',
    device='ch4',
    netmod='ucx',
    with_ucx='/usr/local/ucx',
    prefix='/usr/local/mpich',
    fortran=False,
    hydra=True,
    ldconfig=True,
    configure_opts=['--without-bfd']
)

# OSU Micro-Benchmarks 7.5.2 (Sintaxe de CFLAGS corrigida com aspas internas)
Stage0 += hpccm.building_blocks.generic_autotools(
    build_environment={
        'CC': '/usr/local/mpich/bin/mpicc',
        'CXX': '/usr/local/mpich/bin/mpicxx',
        'CFLAGS': '"-O3 -fPIC"',
        'CXXFLAGS': '"-O3 -fPIC"'
    },
    enable_cuda=False,
    prefix='/usr/local/osu',
    url='https://mvapich.cse.ohio-state.edu/download/mvapich/osu-micro-benchmarks-7.5.2.tar.gz'
)

# ==========================================
# ESTÁGIO 1: RUNTIME (Imagem Final)
# ==========================================
Stage1 += hpccm.primitives.baseimage(image='ubuntu:24.04')

Stage1 += hpccm.building_blocks.packages(ospackages=[
    'libnuma1', 'libhwloc15', 'libxml2', 'libpciaccess0', 'ca-certificates',
    'libibverbs1', 'librdmacm1', 'ibverbs-providers', 'zlib1g', 'libzstd1',
    'libbinutils'
])

Stage1 += hpccm.primitives.copy(_from='devel', src='/usr/local/ucx', dest='/usr/local/ucx')
Stage1 += hpccm.primitives.copy(_from='devel', src='/usr/local/mpich', dest='/usr/local/mpich')
Stage1 += hpccm.primitives.copy(_from='devel', src='/usr/local/osu', dest='/usr/local/osu')

Stage1 += hpccm.primitives.shell(commands=[
    'echo "/usr/local/ucx/lib" > /etc/ld.so.conf.d/hpc.conf',
    'echo "/usr/local/mpich/lib" >> /etc/ld.so.conf.d/hpc.conf',
    'ldconfig'
])

base_osu = '/usr/local/osu/libexec/osu-micro-benchmarks'
Stage1 += hpccm.primitives.environment(variables={
    'PATH': f'/usr/local/mpich/bin:/usr/local/ucx/bin:{base_osu}:{base_osu}/mpi/pt2pt:{base_osu}/mpi/collective:{base_osu}/mpi/one-sided:$PATH',
    'LD_LIBRARY_PATH': '/usr/local/mpich/lib:/usr/local/ucx/lib:$LD_LIBRARY_PATH',
    'UCX_TLS': 'rc_mlx5,ud_mlx5,rc,ud,sm,self'
})

print(Stage0)
print(Stage1)