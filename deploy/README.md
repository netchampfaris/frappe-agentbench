# Deployment

The benchmark runs on its own Frappe Cloud v2 VM ("Agent Bench", team Netchamp,
Ubuntu 24.04, 4 vCPU / 16 GB). The VM has no public IPv4 address. The Frappe
Cloud proxy in Mumbai routes https://agentbench.netchamp.dev to it, and Caddy on
the VM holds the certificate.

```
 agentbench.netchamp.dev            Frappe Cloud proxy              Agent Bench VM
 CNAME proxy.bom.frappe.cloud ──▶  (passes TLS through) ──▶  Caddy :443 ──▶ 127.0.0.1:8080 ──▶ dashboard/
                                                                                        ▲
                                     ./run.sh claude ... ──▶ jobs/ ──▶ report.py --json dashboard/results.json
```

## Routing

1. A Frappe Cloud v2 **Site Domain** record maps the hostname to the VM:
   `route_type` Domain, region `bom`, the VM's server name, and its mesh IPv6
   address. The record must be **Active**.
2. A DNS-only (not proxied) CNAME points `agentbench.netchamp.dev` at
   `proxy.bom.frappe.cloud`.
3. Caddy gets a Let's Encrypt certificate with the TLS-ALPN-01 challenge on
   port 443. HTTP-01 does not work: the proxy answers port 80 itself with a
   redirect to HTTPS.

## Setup on a fresh VM

As root:

```sh
apt-get install -y docker.io docker-compose-v2 docker-buildx git python3
# Caddy 2.7 or newer, from https://caddyserver.com/docs/install#debian-ubuntu-raspbian
# (Ubuntu's own package is too old for the proxy_protocol listener)
cp deploy/Caddyfile /etc/caddy/Caddyfile && systemctl reload caddy
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

mkdir -p ~/.config/systemd/user
cp deploy/agentbench-dashboard.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now agentbench-dashboard
```

## Running benchmarks

```sh
ssh agentbench                  # from forge-next; see ~/.ssh/config there
sudo -iu agentbench
cd ~/frappe-agentbench && ./run.sh claude claude-opus-5-5 -k 3
```

Every agent run refreshes `dashboard/results.json`, so the dashboard shows new
results as soon as the run ends.
