#!/bin/sh
cd "$(dirname "$0")"
python3 bexe-browser.py & PID=$!
trap 'kill $PID 2>/dev/null' EXIT
sleep 1
chromium --app=http://127.0.0.1:8765/ --disable-extensions >/dev/null 2>&1
