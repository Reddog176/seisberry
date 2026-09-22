#!/usr/bin/env bash
set -euxo pipefail

ARCH=$(uname -m)
case "$ARCH" in
  x86_64|amd64|aarch64|arm64)
    ;;
  *)
    echo "Seisberry live streaming requires a 64-bit runtime (detected: $ARCH)." >&2
    exit 1
    ;;
esac

REPO_DIR="${1:-$(pwd)}"
APP_DIR="/opt/seisberry/app"
VENV_DIR="/opt/seisberry/venv"

sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-dev python3-venv git

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/pip" install numpy obspy

sudo mkdir -p "$APP_DIR"
if [ -d "$REPO_DIR" ]; then
    sudo rsync -a --delete "$REPO_DIR/" "$APP_DIR/"
fi

sudo install -d -m 755 /etc/systemd/system
sudo install -m 644 "$APP_DIR/streaming/systemd/seisberry-live.service" /etc/systemd/system/seisberry-live.service

sudo systemctl daemon-reload
sudo systemctl enable --now seisberry-live.service

printf '\nSeisberry live service installed.\n'
printf 'Config file: %s\n' "$APP_DIR/streaming/config.toml"
printf 'Logs: journalctl -u seisberry-live -f\n'
