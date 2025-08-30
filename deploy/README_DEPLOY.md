# Deployment (Debian/Ubuntu, systemd)

## 1) Prepare server
- Ubuntu 22.04+ recommended
- Open outbound internet

## 2) Copy project to server
```bash
# on server, clone or rsync project into /workspace or desired path
# this README assumes project is present at /workspace
```

## 3) Install as systemd service
```bash
sudo bash deploy/install.sh
```
The script will:
- Install Python packages
- Create system user `marketbot` and directory `/opt/marketbot`
- Sync project files into `/opt/marketbot`
- Create venv and install requirements
- Create `/opt/marketbot/.env` if missing
- Install and start systemd unit `marketbot.service`

## 4) Configure token and restart
```bash
sudo nano /opt/marketbot/.env
# set BOT_TOKEN=...
sudo systemctl restart marketbot
```

## 5) Logs and status
```bash
sudo systemctl status marketbot | cat
journalctl -u marketbot -f
```

## 6) Update rollout
```bash
# Pull new version to /workspace then:
sudo rsync -a --delete --exclude .venv --exclude __pycache__/ /workspace/ /opt/marketbot/
sudo chown -R marketbot:marketbot /opt/marketbot
sudo -u marketbot /opt/marketbot/.venv/bin/pip install -r /opt/marketbot/requirements.txt
sudo systemctl restart marketbot
```