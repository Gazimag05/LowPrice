#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/deploy_native.sh user@host BOT_TOKEN [/opt/pricebot]
TARGET="${1:-}"
BOT_TOKEN="${2:-}"
REMOTE_DIR="${3:-/opt/pricebot}"
SERVICE_NAME=pricebot

if [[ -z "${TARGET}" || -z "${BOT_TOKEN}" ]]; then
	echo "Usage: $0 user@host BOT_TOKEN [/opt/pricebot]" >&2
	exit 1
fi

# 1) Upload sources
rsync -avz --delete --exclude .git --exclude .venv . "${TARGET}:${REMOTE_DIR}/"

# 2) Prepare and run on server
ssh -o BatchMode=yes "${TARGET}" bash -s <<EOF
set -euo pipefail
sudo apt update -y
sudo apt install -y python3 python3-pip

cd "${REMOTE_DIR}"

# Write .env
cat > .env <<EENV
BOT_TOKEN=${BOT_TOKEN}
ALLOWED_CHATS=
WB_DEST=-1257786
WB_CURR=rub
WB_APP_TYPE=1
EENV

# Install deps (system-wide or user)
pip3 install --user -r requirements.txt

# Install systemd unit
sudo cp deploy/${SERVICE_NAME}.service /etc/systemd/system/${SERVICE_NAME}.service
sudo systemctl daemon-reload
sudo systemctl enable --now ${SERVICE_NAME}

echo "Deployed via systemd. Logs: journalctl -u ${SERVICE_NAME} -f"
EOF

echo "OK: Deployed to \\"${TARGET}\\" at \\"${REMOTE_DIR}\\""