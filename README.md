## Helpful RunPod Setup Commands
```bash
apt-get update && \
apt-get -y install vim && \
apt-get -y install less && \
apt-get -y install tmux
```

```bash
wget https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh && \
bash Mambaforge-Linux-x86_64.sh -b && \
mambaforge/bin/mamba init bash && \
exec bash
```

```bash
git clone https://github.com/jmsdao/mats5.git && cd mats
```

```bash
mamba env create -f environment.yaml && mamba activate mats
```
