#!/bin/bash
sudo apt update
sudo apt install -y \
    build-essential \
    libmysqlclient-dev \
    libssl-dev \
    libpq-dev \
    python3.9 \
    python3.9-venv \
    python3.9-dev

pip install -r requirements.txt

