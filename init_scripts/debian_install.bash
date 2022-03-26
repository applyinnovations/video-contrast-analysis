#!/usr/bin/env bash

# Install requirements on debian, then instantiate 2 services and run them

set -aeuo pipefail

declare -r VENV='/opt/vca/vca_venv' # Python virtual environment
declare -r VARS='/opt/vca/var' # Working directory, where to put auth ini &etc.
declare -r VCA_SERVICE='vca.service'
declare -r SERVICE='vca.service'
declare -r VCA_BUCKET_SERVICE='vca_bucket.service'

sudo apt-get update -qq
sudo apt-get install -y git ffmpeg libsm6 libxext6 python3-opencv python3-venv python3-pip
sudo python3 -m pip install -U pip
sudo python3 -m pip install -U setuptools wheel
sudo mkdir -p "$VENV" "$VARS"
sudo chown -R "$USER":"$(id -gn)" "$VENV" "$VARS"
python3 -m venv --system-site-packages "$VENV"

cd "$VARS"  # Working directory
curl -OL 'https://raw.githubusercontent.com/applyinnovations/video-contrast-analysis/master/requirements.txt'
sed -i '/opencv-python/d' 'requirements.txt'  # python3-opencv is installed above and included with `--system-site-packages`
"$VENV"'/bin/python' -m pip install -r "$VARS"'/requirements.txt'
"$VENV"'/bin/python' -m pip install -e 'git+https://github.com/applyinnovations/video-contrast-analysis@server#egg=video_contrast_analysis'

sed 's|VENV|'"$VENV"'|g; s|VARS|'"$VARS"'|g' "$VENV"'/src/video-contrast-analysis/init_scripts/'"$VCA_SERVICE" > "$VCA_SERVICE"
sudo cp "$VCA_SERVICE" '/etc/systemd/system/'"$VCA_SERVICE"
sudo cp "$VCA_SERVICE" '/etc/systemd/system/'"$VCA_BUCKET_SERVICE"
sudo sed -i 's/server/gcloud_bucket_proc/g ; s/^Description=.*/Description=vca_bucket/' '/etc/systemd/system/'"$VCA_BUCKET_SERVICE"

sudo systemctl daemon-reload
for service in "$SERVICE" "$VCA_SERVICE"; do
  ( sudo systemctl enable "$service" && sudo systemctl start "$service" ) &
  # ( sleep 30 && journalctl --no-pager -u "$service" -n 100 ) &
done
