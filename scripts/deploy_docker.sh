#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/deploy_docker.sh user@host BOT_TOKEN [/opt/pricebot]
TARGET="${1:-}"
BOT_TOKEN="${2:-}"
REMOTE_DIR="${3:-/opt/pricebot}"

if [[ -z "${TARGET}" || -z "${BOT_TOKEN}" ]]; then
	echo "Usage: $0 user@host BOT_TOKEN [/opt/pricebot]" >&2
	exit 1
fi

# 1) Upload sources
rsync -avz --delete --exclude .git --exclude .venv . "${TARGET}:${REMOTE_DIR}/"

# 2) Prepare and run on server
ssh -o BatchMode=yes "${TARGET}" bash -s <<EOF
set -euo pipefail

# Ensure docker
if ! command -v docker >/dev/null 2>&1; then
	curl -fsSL https://get.docker.com | sh
fi

cd "${REMOTE_DIR}"

# Write .env if not exists; otherwise update BOT_TOKEN
if [[ ! -f .env ]]; then
	cat > .env <<EENV
BOT_TOKEN=${BOT_TOKEN}
ALLOWED_CHATS=
WB_DEST=-1257786
WB_CURR=rub
WB_APP_TYPE=1
EENV
else
	sed -i "s/^BOT_TOKEN=.*/BOT_TOKEN=${BOT_TOKEN}/" .env || echo "BOT_TOKEN=${BOT_TOKEN}" >> .env
fi

# Build & run
/docker/bin/true 2>/dev/null || true
if docker compose version >/dev/null 2>&1; then
	docker compose up -d --build
else
	docker-compose up -d --build
fi

echo "Deployed via Docker. Logs: docker compose logs -f"
EOF

echo "OK: Deployed to \\"${TARGET}\\" at \\"${REMOTE_DIR}\\""