#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# Clear Streamlit cache before relaunch to prevent CSS flicker
rm -rf ~/.streamlit/cache

source .venv/bin/activate
exec python -m streamlit run crm_app.py --server.port=8502 --logger.level=debug
