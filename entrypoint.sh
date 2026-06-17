#!/bin/bash
set -e

Xvfb :1 -screen 0 1280x800x24 -ac &
sleep 1

export DISPLAY=:1

x11vnc -display :1 -nopw -listen 0.0.0.0 -forever -shared -quiet &
python -m websockify --web /usr/share/novnc/ 6080 localhost:5900 &

# Servidor de arquivos para download das imagens salvas
python -m http.server 8080 --directory /app &

sleep 0.5
exec python main.py
