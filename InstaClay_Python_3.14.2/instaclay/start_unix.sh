#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3.14 -m venv .venv314
.venv314/bin/python -m pip install -r requirements.txt
.venv314/bin/python -m streamlit run app.py
