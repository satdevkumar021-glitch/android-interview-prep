#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "🤖 Starting Android Interview Mastery Web App..."
echo "📍 Directory: $DIR"
# Get Local LAN IP
LAN_IP=$(ipconfig getifaddr en0 2>/dev/null || ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1)

echo "🌐 Local Computer URL : http://localhost:8080"
if [ -n "$LAN_IP" ]; then
    echo "📱 Mobile (Same Wi-Fi) : http://$LAN_IP:8080"
fi
echo "--------------------------------------------------"

# Check if port 8080 is already active
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚡ Server already running on port 8080!"
else
    python3 -m http.server 8080 --bind 0.0.0.0 &
    sleep 1
fi

open http://localhost:8080
echo "✅ App launched in your default browser!"
