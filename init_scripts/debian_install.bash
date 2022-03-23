#!/usr/bin/env bash

set -aeuo pipefail

declare -r VENV='/opt/vca_venv' # Python virtual environment
declare -r VARS='/opt/vca_vars' # Working directory, where to put auth ini &etc.
declare -r SERVICE='vca.service'

sudo apt-get update -qq
sudo apt-get install -y ffmpeg libsm6 libxext6 python3-opencv python3-venv
sudo python3 -m pip install -U pip
sudo python3 -m pip install -U setuptools wheel
sudo mkdir -p "$VENV" "$VARS"
sudo chown -R $USER:$GROUP "$VENV" "$VARS"
python3 -m venv --system-site-packages "$VENV"
"$VENV"'/bin/python' -m pip install -e 'git+https://github.com/applyinnovations/video-contrast-analysis@server#egg=video_contrast_analysis'

sudo sed 's|VENV|'"$VENV"'|g; s|VARS|'"$VARS"'|g' "$SERVICE" > '/etc/systemd/system/'"$SERVICE"
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE"
sudo systemctl start "$SERVICE"
