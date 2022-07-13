#!/usr/bin/env bash

# Install requirements on debian, then instantiate 2 services and run them

set -vaeuo pipefail

declare -r VENV='/opt/vca/vca_venv' # Python virtual environment
declare -r VARS='/opt/vca/var' # Working directory, where to put auth ini &etc.
declare -r VCA_SERVICE='vca.service'
declare -r VCA_BUCKET_SERVICE='vca_bucket.service'

# install google ops agent
curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
sudo bash add-google-cloud-ops-agent-repo.sh --also-install

sudo apt-get update -qq
sudo apt-get install -y git ffmpeg libsm6 libxext6 python3-venv python3-pip cython3

# install python3-opencv from source to get latest version
sudo apt-get install -y build-essential cmake git pkg-config libgtk-3-dev \
    libavcodec-dev libavformat-dev libswscale-dev libv4l-dev \
    libxvidcore-dev libx264-dev libjpeg-dev libpng-dev libtiff-dev \
    gfortran openexr libatlas-base-dev python3-dev python3-numpy \
    libtbb2 libtbb-dev libdc1394-22-dev
mkdir /opt/opencv_build && cd /opt/opencv_build
git clone https://github.com/opencv/opencv.git
git clone https://github.com/opencv/opencv_contrib.git
cd opencv && mkdir build && cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D INSTALL_C_EXAMPLES=ON \
    -D INSTALL_PYTHON_EXAMPLES=ON \
    -D OPENCV_GENERATE_PKGCONFIG=ON \
    -D OPENCV_EXTRA_MODULES_PATH=/opt/opencv_build/opencv_contrib/modules \
    -D BUILD_EXAMPLES=ON ..
make -j$(nproc)
sudo make install
# finised python3-opencv install

sudo -H python3 -m pip install -U setuptools wheel
sudo -H python3 -m pip install -U pip
sudo mkdir -p "$VENV" "$VARS"
sudo chown -R "$(id -un)":"$(id -gn)" "$VENV" "$VARS"
python3 -m venv --system-site-packages "$VENV"

cd "$VARS"  # Working directory
"$VENV"'/bin/python' -m pip install --upgrade pip
curl -OL 'https://raw.githubusercontent.com/applyinnovations/video-contrast-analysis/master/requirements.txt'
sed -i '/opencv-python/d' 'requirements.txt'  # python3-opencv is installed above and included with `--system-site-packages`
"$VENV"'/bin/python' -m pip install -r "$VARS"'/requirements.txt'
"$VENV"'/bin/python' -m pip install -e 'git+https://github.com/applyinnovations/video-contrast-analysis@master#egg=video_contrast_analysis'

sed 's|VENV|'"$VENV"'|g; s|VARS|'"$VARS"'|g' "$VENV"'/src/video-contrast-analysis/init_scripts/'"$VCA_SERVICE" > "$VCA_SERVICE"
sudo cp "$VCA_SERVICE" '/etc/systemd/system/'"$VCA_SERVICE"
sudo cp "$VCA_SERVICE" '/etc/systemd/system/'"$VCA_BUCKET_SERVICE"
sudo sed -i 's/server/gcloud_bucket_proc/g ; s/^Description=.*/Description=vca_bucket/' '/etc/systemd/system/'"$VCA_BUCKET_SERVICE"

sudo systemctl daemon-reload
sudo systemctl enable "$VCA_SERVICE"
sudo systemctl start "$VCA_SERVICE"
sudo systemctl enable "$VCA_BUCKET_SERVICE"
sudo systemctl start "$VCA_BUCKET_SERVICE"
