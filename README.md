# README — Execução dos Benchmarks OSU

Este documento descreve o processo completo para reproduzir os benchmarks OSU Micro-Benchmarks utilizando Spack para gerenciamento de dependências e Apptainer para criação da imagem de container.

---

## 1. Ativando o Ambiente Spack

Coloque os arquivos `spack.yaml` e `spack.lock` na mesma pasta no novo sistema.

### Método 1: Ambiente Local

**1.** Navegar até a pasta dos arquivos:

```bash
cd /caminho/para/pasta_do_ambiente
```

**2.** Ativar o ambiente local:

```bash
spack env activate .
```

**3.** Instalar o ambiente:

```bash
spack install
```

Como o `spack.lock` está na mesma pasta, o Spack utilizará exatamente os mesmos hashes, versões e dependências do ambiente original.

### Método 2: Ambiente Nomeado

Caso prefira gerenciar o ambiente pelo nome (como `cenapad_challenge`), siga estes passos:

**1.** Criar o novo ambiente nomeado:

```bash
spack env create novo_ambiente /caminho/para/spack.yaml
```

**2.** Copiar o `spack.lock` para garantir reprodução exata:

```bash
cp /caminho/para/spack.lock $(spack location -e novo_ambiente)/
```

> **Nota:** Se ignorar o `spack.lock`, o Spack refará a concretização e poderá baixar versões diferentes de dependências.

**3.** Ativar o ambiente:

```bash
spack env activate novo_ambiente
spack install
```

---

## 2. Instalando o Spack do Zero

Se precisar instalar o Spack e configurar o ambiente manualmente:

```bash
# Baixar o Spack e criar o ambiente
git clone -c feature.experimentalGpgEngine=false https://github.com/spack/spack.git ~/spack
source ~/spack/share/spack/setup-env.sh

# Criar e ativar o ambiente
spack env create cenapad_challenge
spack env activate cenapad_challenge

# Instalar os pacotes necessários
spack add ucx+mlx5_dv+rc+rdmacm+verbs ^rdma-core
spack add mpich device=ch4 netmod=ucx ^ucx+mlx5_dv+rc+rdmacm+verbs
spack add osu-micro-benchmarks ^mpich device=ch4 netmod=ucx

# Concretizar e instalar
spack concretize -f
spack install
spack spec -l > spack_spec_concretized.txt
```

---

## 3. Criando a Imagem Apptainer

É necessário ter o Python instalado.

```bash
# Gerar o arquivo de definição
hpccm --recipe osu_benchmark.py --format singularity --singularity-version 3.8 > Apptainer.def

# Construir a imagem
sudo apptainer build osu_benchmarks.sif Apptainer.def
```

---

## 4. Executando no HPC

Copie o conteúdo para o cluster HPC e submeta o job:

```bash
qsub submit_osu.pbs
```

---

## 5. Analisando os Resultados

Para verificar os resultados dos experimentos conforme descrito no [main.pdf](main.pdf), instale as dependências do [requirements.txt](requeriments.txt) e execute os notebooks Jupyter, ajustando o caminho para a pasta onde estão os logs de resultado.