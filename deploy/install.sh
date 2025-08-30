#!/usr/bin/env bash
set -euo pipefail

APP_DIR=/opt/marketbot
SERVICE_NAME=marketbot
SERVICE_FILE=/etc/systemd/system/${SERVICE_NAME}.service

if [[ $EUID -ne 0 ]]; then
	echo "Please run as root (sudo)." >&2
	exit 1
fi

# Packages
apt-get update -y
apt-get install -y python3 python3-venv python3-pip git

# User and directory
id -u marketbot >/dev/null 2>&1 || useradd --system --create-home --home-dir ${APP_DIR} --shell /usr/sbin/nologin marketbot
mkdir -p ${APP_DIR}
chown -R marketbot:marketbot ${APP_DIR}

# Sync files
rsync -a --delete --exclude .venv --exclude __pycache__/ /workspace/ ${APP_DIR}/
chown -R marketbot:marketbot ${APP_DIR}

# Venv and deps
sudo -u marketbot bash -c "python3 -m venv ${APP_DIR}/.venv && ${APP_DIR}/.venv/bin/python -m pip install --upgrade pip && ${APP_DIR}/.venv/bin/pip install -r ${APP_DIR}/requirements.txt"

# Env file
if [[ ! -f ${APP_DIR}/.env ]]; then
	echo "BOT_TOKEN=PUT_YOUR_TOKEN_HERE" > ${APP_DIR}/.env
	chown marketbot:marketbot ${APP_DIR}/.env
fi

# systemd unit
install -m 0644 /workspace/deploy/marketbot.service ${SERVICE_FILE}
systemctl daemon-reload
systemctl enable ${SERVICE_NAME}
systemctl restart ${SERVICE_NAME}

# Status
systemctl --no-pager status ${SERVICE_NAME} | cat

echo "\nInstalled. Edit ${APP_DIR}/.env with your BOT_TOKEN and restart: systemctl restart ${SERVICE_NAME}"