#!/bin/sh
# Build the content and serve the app on your local network.
cd "$(dirname "$0")/.." || exit 1
node scripts/build.mjs || exit 1
IP=$(ipconfig getifaddr en0 2>/dev/null || echo localhost)
echo "On this Mac:    http://localhost:8000"
echo "On your iPhone: http://$IP:8000  (same Wi-Fi)"
python3 -m http.server 8000
