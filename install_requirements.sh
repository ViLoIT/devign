#! /bin/env bash

# Install the required packages
python3 -m venv venv
source ./venv/bin/activate

pip install pandas numpy scikit-learn
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install torch_geometric pyg_lib torch_scatter torch_sparse torch_cluster torch_spline_conv -f https://data.pyg.org/whl/torch-2.5.0+cpu.html
pip install gensim
pip install cpgclientlib