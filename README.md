## Helpful RunPod Setup Commands
```bash
# Install some linux tools
apt-get update && \
apt-get -y install vim && \
apt-get -y install less && \
apt-get -y install tmux && \

# Install mamba
wget https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh && \
bash Mambaforge-Linux-x86_64.sh -b && \
mambaforge/bin/mamba init bash && \
exec bash && \

# Clone and cd into repo
git clone https://github.com/jmsdao/mats5.git && cd mats5 && \

# Install and eactivate env
mamba env create -f environment.yaml && mamba activate mats
```
