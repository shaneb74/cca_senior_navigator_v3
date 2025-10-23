#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
source venv/bin/activate
exec python -m streamlit run app.py --logger.level=debug
