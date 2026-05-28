#!/bin/bash
# Deploy drillbot to Raspberry Pi
# Usage: ./deploy.sh [--restart]

PI_USER="drillbotics"
# Static IP on rig Ethernet network
PI_HOST="10.10.10.20"
PI_PATH="~/drillbot"
PI_TARGET="${PI_USER}@${PI_HOST}:${PI_PATH}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Deploying to ${PI_TARGET}..."

# Sync app code and scripts (exclude data, __pycache__, etc.)
rsync -avz --progress \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.git' \
    --exclude 'data/*.db' \
    --exclude '.env' \
    --exclude 'venv' \
    --exclude '.venv' \
    "${SCRIPT_DIR}/app" \
    "${SCRIPT_DIR}/scripts" \
    "${SCRIPT_DIR}/docs" \
    "${PI_TARGET}/"

echo ""
echo "Files synced."

# Optionally restart the service
if [[ "$1" == "--restart" ]]; then
    echo "Restarting drillbot service..."
    ssh "${PI_USER}@${PI_HOST}" "cd ${PI_PATH} && pkill -f 'uvicorn.*api:app' || true && nohup uvicorn app.api:app --host 0.0.0.0 --port 8000 > drillbot.log 2>&1 &"
    echo "Service restarted."
fi

echo ""
echo "Done! Test with:"
echo "  curl http://${PI_HOST}:8000/health"
echo ""
echo "To pull the new model on the Pi:"
echo "  ssh ${PI_USER}@${PI_HOST} 'ollama pull qwen2:0.5b'"
