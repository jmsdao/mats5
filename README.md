## Handy Dandy Snippets
```bash
# Install some linux tools
apt-get update && \
apt-get -y install vim && \
apt-get -y install less && \
apt-get -y install tmux
```

```bash
# Install mamba
wget https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh && \
bash Mambaforge-Linux-x86_64.sh -b && \
mambaforge/bin/mamba init bash && \
exec bash
```

```bash
# Clone and cd into repo
git clone https://github.com/jmsdao/mats5.git && cd mats5
```

```bash
# Install and activate env (fresh)
mamba env create -f environment.yaml && mamba activate mats
```

```bash
# Activate env from runpod workspace
mamba activate /workspace/mamba-envs/mats
```

```python
# Handy snippet to get repo root from anywhere in the repo
import sys
from subprocess import check_output
ROOT = check_output('git rev-parse --show-toplevel', shell=True).decode("utf-8").strip()
if ROOT not in sys.path: sys.path.append(ROOT)
```
