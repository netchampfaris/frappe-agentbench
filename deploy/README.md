# Deployment

The benchmark runs on its own Frappe Cloud v2 VM ("Agent Bench", team Netchamp,
Ubuntu 24.04, 4 vCPU / 16 GB). It serves the dashboard at
https://agentbench.netchamp.dev through a Cloudflare tunnel, so the VM needs no
open ports.

```
 agentbench.netchamp.dev ──▶ Cloudflare tunnel ──▶ VM 127.0.0.1:8080 ──▶ dashboard/
                                                    ▲
                     ./run.sh claude ... ──▶ jobs/ ─┴─ report.py --json dashboard/results.json
```

## Setup on a fresh VM

As root:

```sh
apt-get install -y docker.io docker-compose-v2 docker-buildx git python3
# cloudflared: https://github.com/cloudflare/cloudflared/releases
useradd -m -s /bin/bash -G docker agentbench
loginctl enable-linger agentbench
```

As `agentbench`:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/netchampfaris/frappe-agentbench ~/frappe-agentbench
cd ~/frappe-agentbench
cp .env.example .env            # add CLAUDE_CODE_OAUTH_TOKEN
./run.sh build && ./run.sh check

# Tunnel: copy the agentbench tunnel's credentials JSON to ~/.cloudflared/,
# then write ~/.cloudflared/config.yml from cloudflared.example.yml.
mkdir -p ~/.config/systemd/user
cp deploy/*.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now agentbench-dashboard agentbench-tunnel
```

## Running benchmarks

```sh
ssh agentbench                  # from forge-next; see ~/.ssh/config there
sudo -iu agentbench
cd ~/frappe-agentbench && ./run.sh claude claude-opus-5-5 -k 3
```

Every agent run refreshes `dashboard/results.json`, so the dashboard shows new
results as soon as the run ends.
