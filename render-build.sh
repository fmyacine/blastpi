#!/usr/bin/env bash
set -o errexit

# Upgrade pip & install deps
pip install --upgrade pip
pip install -r requirements.txt
