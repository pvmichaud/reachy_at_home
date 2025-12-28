#!/bin/bash
set -e

echo "Deploying latest code..."

cd ~/reachy-assistant

# Pull latest
git pull origin main

# Activate venv
source venv/bin/activate

# Install any new dependencies
pip install -r requirements.txt --quiet

# Restart services
sudo systemctl restart reachy-assistant || echo "Service not yet configured"
sudo systemctl restart reachy-api || echo "Service not yet configured"

echo "Deploy complete!"
