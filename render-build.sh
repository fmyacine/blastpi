#!/usr/bin/env bash
# fail on error
set -o errexit

# Install Rust (needed for cryptography/orjson/etc.)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source $HOME/.cargo/env

# Then install Python deps
pip install --upgrade pip
pip install -r requirements.txt
