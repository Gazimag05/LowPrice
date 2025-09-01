## VPS Deployment Guide

Two options:
- Docker (recommended)
- Native (systemd)

### 1) Prepare server
- Ubuntu/Debian, ports open for outbound HTTPS.
- Create bot user (optional for native):
```bash
sudo adduser --system --group --home /opt/pricebot pricebot
```

### 2) Upload files to VPS
On your local machine (from project root):
```bash
# Copy sources (adjust HOST/IP and path)
rsync -avz --delete . user@HOST:/opt/pricebot/
```

### 3A) Run with Docker (recommended)
Install Docker & Compose:
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# relogin or: newgrp docker
```

Configure env:
```bash
cd /opt/pricebot
cp .env.example .env
nano .env   # set BOT_TOKEN
```

Build & start:
```bash
cd /opt/pricebot
docker compose up -d --build
```

Logs:
```bash
docker compose logs -f
```

### 3B) Run natively with systemd
Install Python:
```bash
sudo apt update && sudo apt install -y python3 python3-pip
```

Copy to working dir and set env:
```bash
sudo mkdir -p /opt/pricebot
sudo rsync -avz --delete . /opt/pricebot/
sudo cp /opt/pricebot/.env.example /opt/pricebot/.env
sudo nano /opt/pricebot/.env   # set BOT_TOKEN
```

Create service:
```bash
sudo cp /opt/pricebot/deploy/pricebot.service /etc/systemd/system/pricebot.service
sudo chown -R pricebot:pricebot /opt/pricebot || true
```

Reload & start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now pricebot
```

Status & logs:
```bash
systemctl status pricebot
journalctl -u pricebot -f
```

### Update bot (both approaches)
- Pull or rsync new code to `/opt/pricebot`
- Docker: `docker compose up -d --build`
- Native: `sudo systemctl restart pricebot`