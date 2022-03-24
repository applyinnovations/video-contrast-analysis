#!/usr/bin/env bash

set -aeuo pipefail

declare -r VENV='/opt/vca_venv' # Python virtual environment
declare -r VARS='/opt/vca_vars' # Working directory, where to put auth ini &etc.
declare -r VCA_SERVICE='vca.service'
declare -r SERVICE='vca.service'
declare -r VCA_BUCKET_SERVICE='vca_bucket.service'

sudo apt-get update -qq
sudo apt-get install -y ffmpeg libsm6 libxext6 python3-opencv python3-venv
sudo python3 -m pip install -U pip
sudo python3 -m pip install -U setuptools wheel
sudo mkdir -p "$VENV" "$VARS"
sudo chown -R $USER:$GROUP "$VENV" "$VARS"
python3 -m venv --system-site-packages "$VENV"
"$VENV"'/bin/python' -m pip install -r 'https://raw.githubusercontent.com/applyinnovations/video-contrast-analysis/master/requirements.txt'
"$VENV"'/bin/python' -m pip install -e 'git+https://github.com/applyinnovations/video-contrast-analysis@server#egg=video_contrast_analysis'

sudo sed 's|VENV|'"$VENV"'|g; s|VARS|'"$VARS"'|g' "$VCA_SERVICE" > '/etc/systemd/system/'"$VCA_SERVICE"
sudo cp '/etc/systemd/system/'"$VCA_SERVICE" '/etc/systemd/system/'"$VCA_BUCKET_SERVICE"
sudo sed -i 's/server/gcloud_bucket_proc' '/etc/systemd/system/'"$VCA_BUCKET_SERVICE"

sudo systemctl daemon-reload
for service in "$SERVICE" "$VCA_SERVICE"; do
  sudo systemctl enable "$service"
  sudo systemctl start "$service"
  ( sleep 30 && journalctl --no-pager -u "$service" -n 100 ) &
done
