#!/bin/bash
set -e

echo "Starting Endee server in background..."
# Find the ndd binary (could be ndd-avx2, ndd-neon-darwin, etc.)
NDD_BINARY=$(find /app/build -maxdepth 1 -name 'ndd-*' -type f | head -n 1)

if [ -z "$NDD_BINARY" ]; then
    echo "ERROR: No Endee binary found in /app/build/"
    exit 1
fi

echo "Found binary: $NDD_BINARY"
NDD_DATA_DIR=/app/data NDD_AUTH_TOKEN="${NDD_AUTH_TOKEN:-}" "$NDD_BINARY" &

# Wait for Endee to be ready
echo "Waiting for Endee to start..."
for i in $(seq 1 30); do
    if curl -s http://localhost:8080/api/v1/health > /dev/null 2>&1; then
        echo "Endee is ready!"
        break
    fi
    echo "  Attempt $i/30..."
    sleep 2
done

echo "Starting Gradio app on port ${PORT:-7860}..."
cd /app/ai_resume_selector
exec python app.py
