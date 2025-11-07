#!/bin/bash
# Smart CRM Startup Script
# Starts the Concierge Care Advisors CRM on port 8502

echo "🏢 Starting Concierge Care Advisors Smart CRM..."
echo "📊 Dashboard: http://localhost:8502"
echo "⚡ Features: Customer 360°, Smart Timeline, AI Next Steps, Smart Matching"
echo ""

# Start the CRM application
streamlit run crm_app.py --server.port=8502