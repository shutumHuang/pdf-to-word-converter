#!/usr/bin/env bash
# exit on error
set -o errexit

# 安裝依賴
pip install -r requirements.txt

# 建立必要的目錄
mkdir -p /tmp/uploads
mkdir -p /tmp/converted 