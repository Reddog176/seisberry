#!/usr/bin/env bash
set -euxo pipefail

# One-shot Raspberry Pi bootstrap for Seisberry live streaming.
# Intended for a fresh Raspberry Pi OS install.

export DEBIAN_FRONTEND=noninteractive

ARCH=$(uname -m)
case "$ARCH" in
  x86_64|amd64|aarch64|arm64)
    ;;
  *)
    echo "Seisberry live streaming requires a 64-bit runtime (detected: $ARCH)." >&2
    exit 1
    ;;
esac

sudo apt-get update
sudo apt-get install -y --no-install-recommends \
  python3 \
  python3-venv \
  python3-pip \
  python3-dev \
  git \
  rsync \
  curl

if [ ! -d /opt/seisberry ]; then
  sudo mkdir -p /opt/seisberry
fi
sudo chown -R "$USER:$USER" /opt/seisberry

if [ ! -d /opt/seisberry/venv ]; then
  python3 -m venv /opt/seisberry/venv
fi

# install project dependencies
source /opt/seisberry/venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install numpy obspy tomli

# ensure repo is in place
REPO_DIR="${1:-$(pwd)}"
APP_DIR="/opt/seisberry/app"
mkdir -p "$APP_DIR"
if [ -d "$REPO_DIR" ]; then
  rsync -a --delete "$REPO_DIR/" "$APP_DIR/"
fi

# install and enable service
sudo install -d -m 755 /etc/systemd/system
sudo install -m 644 "$APP_DIR/streaming/systemd/seisberry-live.service" /etc/systemd/system/seisberry-live.service
sudo systemctl daemon-reload
sudo systemctl enable --now seisberry-live.service

cat <<EOF

Seisberry Python environment is ready.

Next steps:
  1. Edit /opt/seisberry/app/streaming/config.toml and set simulate_adc = false
  2. Check service status: sudo systemctl status seisberry-live.service
  3. Follow logs: journalctl -u seisberry-live.service -f

EOF
