#!/bin/sh
set -e
sudo dpkg --add-architecture i386
sudo apt-get update
sudo apt-get install -y wine wine32 wine64 xvfb
printf '\nBEXE Linux runtime installed. Run ./bexe-browser.sh\n'
