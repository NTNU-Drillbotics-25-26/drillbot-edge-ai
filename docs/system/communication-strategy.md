# Drillbot Communication Strategy

## Overview

The Drillbot system requires reliable communication between a Raspberry Pi (running the RAG-based drilling assistant) and a Control System PC (running the operator GUI). This document describes the network architecture, the rationale for design decisions, and step-by-step configuration instructions for replication.

## System Components

| Component | Role | Hardware |
|-----------|------|----------|
| Raspberry Pi | Hosts Drillbot API (FastAPI + Ollama LLM) | Raspberry Pi 4/5 |
| Control System PC | Operator GUI with drillbot chat interface | Windows workstation |
| Trajectory System | Path planning computer | Dedicated workstation |
| Network Switch | Connects all rig components | Unmanaged Ethernet switch |

## Network Architecture

### Final Solution: Dedicated Rig Ethernet Network

All rig components communicate over a dedicated Ethernet network using static IP addresses:

```
┌─────────────────────────────────────────────────────────────┐
│                    Rig Ethernet Network                     │
│                      (10.10.10.0/24)                        │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Raspberry Pi │  │  Control PC  │  │  Trajectory  │      │
│  │  10.10.10.20 │  │  10.10.10.5  │  │  10.10.10.4  │      │
│  │    (eth0)    │  │  (Ethernet)  │  │  (Ethernet)  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │               │
│         └────────────┬────┴─────────────────┘               │
│                      │                                      │
│               ┌──────┴──────┐                               │
│               │   Switch    │                               │
│               └─────────────┘                               │
└─────────────────────────────────────────────────────────────┘
                       │
              (No router/gateway)
              (Isolated network)
```

### IP Address Allocation

| Device | IP Address | Interface | Configuration Method |
|--------|------------|-----------|---------------------|
| Raspberry Pi | 10.10.10.20 | eth0 | NetworkManager (static) |
| Control PC | 10.10.10.5 | Ethernet | Windows static IP |
| Trajectory System | 10.10.10.4 | Ethernet | Static |
| Reserved | 10.10.10.1-3 | — | Future expansion |
| Reserved | 10.10.10.6-9 | — | Future expansion |

### Communication Endpoints

| Service | Endpoint | Protocol | Port |
|---------|----------|----------|------|
| Drillbot API | http://10.10.10.20:8000 | HTTP/REST | 8000 |
| Health Check | http://10.10.10.20:8000/health | HTTP GET | 8000 |
| Ask Question | http://10.10.10.20:8000/ask | HTTP POST | 8000 |
| UDP Telemetry | 0.0.0.0:5005 | UDP | 5005 |
| Trajectory (in) | 0.0.0.0:4050 | TCP | 4050 |
| Trajectory (out) | 10.10.10.4:4052 | TCP | 4052 |

## Rationale for Design Decisions

### Why Not WiFi?

The university network (eduroam) was initially considered but rejected for the following reasons:

1. **Dynamic IP Assignment**: Eduroam uses DHCP with dynamic address allocation. IP addresses change when:
   - The device reconnects to the network
   - The DHCP lease expires
   - The device has been disconnected for an extended period

2. **No Static IP Option**: NTNU's wireless network does not support static IP assignment. From NTNU IT documentation:
   > "Merk at det kun kan tildeles fast IP-adresse i kablet nettverk, vi kan ikke sette fast IP-adresse i NTNUs trådløse nett."
   > (Note: Static IP addresses can only be assigned on wired networks; we cannot set static IP addresses on NTNU's wireless network.)

3. **Reliability Requirements**: The drilling control system requires deterministic communication. Network variability introduces unacceptable risk for safety-critical operations.

4. **Latency**: WiFi introduces variable latency (2-10ms typical) compared to wired Ethernet (<1ms).

### Why a Dedicated Rig Network?

1. **Isolation**: The rig network is physically separated from the university network, eliminating interference from other network traffic.

2. **Static Addressing**: All devices use manually configured static IPs, ensuring consistent connectivity.

3. **No External Dependencies**: The rig network functions without internet access or external infrastructure.

4. **Existing Infrastructure**: The Control PC and Trajectory System already used the 10.10.10.0/24 subnet; the Raspberry Pi was added to this existing network.

### Why 10.10.10.0/24?

The 10.10.10.0/24 subnet was chosen because:
- It was already in use by existing rig components (Trajectory System, Control PC)
- It falls within the RFC 1918 private address space (10.0.0.0/8)
- The /24 subnet provides 254 usable addresses, sufficient for the rig with room for expansion

## Configuration Instructions

### Raspberry Pi Configuration

#### 1. NetworkManager Connection Setup

The Raspberry Pi uses NetworkManager to manage network interfaces. The Ethernet connection is configured with a static IP:

```bash
# View existing connections
nmcli con show

# Modify the Ethernet connection (named "drill-link")
sudo nmcli con modify "drill-link" ipv4.addresses "10.10.10.20/24" ipv4.method manual

# Activate the connection
sudo nmcli con up "drill-link"

# Verify configuration
ip addr show eth0
```

Expected output:
```
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP
    inet 10.10.10.20/24 brd 10.10.10.255 scope global noprefixroute eth0
       valid_lft forever preferred_lft forever
```

#### 2. Systemd Service Configuration

The Drillbot API runs as a systemd service for automatic startup and crash recovery:

```bash
# Create service file
sudo tee /etc/systemd/system/drillbot.service << 'EOF'
[Unit]
Description=Drillbot RAG API
After=network.target

[Service]
Type=simple
User=drillbotics
WorkingDirectory=/home/drillbotics/drillbot
ExecStart=/home/drillbotics/drillbot/venv/bin/uvicorn app.api:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable drillbot
sudo systemctl start drillbot

# Verify status
sudo systemctl status drillbot
```

#### 3. Verification Commands

```bash
# Check service status
sudo systemctl status drillbot

# View service logs
sudo journalctl -u drillbot -f

# Check network configuration
ip addr show eth0
nmcli con show "drill-link"

# Test API locally
curl http://localhost:8000/health
```

### Control PC Configuration

The Control PC (Windows) uses a static IP configuration on its Ethernet adapter:

| Setting | Value |
|---------|-------|
| IP Address | 10.10.10.5 |
| Subnet Mask | 255.255.255.0 |
| Default Gateway | (none) |
| DHCP | Disabled |

Configuration path: Settings → Network & Internet → Ethernet → Edit IP settings

#### Verification Commands (PowerShell)

```powershell
# Check Ethernet adapter configuration
ipconfig /all | Select-String -Pattern "Ethernet" -Context 0,15

# Test connectivity to Raspberry Pi
ping 10.10.10.20

# Test Drillbot API
curl http://10.10.10.20:8000/health

# Test question endpoint
Invoke-RestMethod -Uri "http://10.10.10.20:8000/ask" -Method POST -ContentType "application/json" -Body '{"question": "What is WOB?"}'
```

### GUI Configuration

The Drillbotics GUI configuration file (`config.py`) specifies the Drillbot connection:

```python
# --- DRILLBOT (RAG ASSISTANT) ---
# Static IP on rig Ethernet network (10.10.10.x)
DRILLBOT_PI_HOST = "10.10.10.20"
DRILLBOT_PI_PORT = 8000
DRILLBOT_API_URL = f"http://{DRILLBOT_PI_HOST}:{DRILLBOT_PI_PORT}/ask"
DRILLBOT_HEALTH_URL = f"http://{DRILLBOT_PI_HOST}:{DRILLBOT_PI_PORT}/health"
DRILLBOT_TIMEOUT = 120  # seconds
```

## API Protocol

### Health Check

```
GET /health

Response:
{
    "status": "ok",
    "model": "qwen2.5:1.5b",
    "retrieval_mode": "fts",
    "cache_enabled": true,
    "cache_size": 0,
    "cache_max": 64
}
```

### Ask Question

```
POST /ask
Content-Type: application/json

Request:
{
    "question": "What is the recommended WOB for this formation?",
    "ui_context": {
        "current_wob": 15.5,
        "current_rpm": 120
    }
}

Response:
{
    "answer": "Based on the documentation...",
    "sources": ["docs/drilling-parameters.md"],
    "chunks_used": 3,
    "timing": {
        "retrieval_ms": 12,
        "llm_ms": 450,
        "total_ms": 462
    }
}
```

## Troubleshooting

### Pi Not Reachable

1. Verify physical connection (Ethernet cable, switch)
2. Check Pi's IP: `ip addr show eth0`
3. Check NetworkManager connection: `nmcli con show`
4. Restart networking: `sudo nmcli con up "drill-link"`

### Drillbot Service Not Running

1. Check status: `sudo systemctl status drillbot`
2. View logs: `sudo journalctl -u drillbot -n 50`
3. Restart service: `sudo systemctl restart drillbot`

### Connection Timeout from GUI

1. Verify network: `ping 10.10.10.20` from Control PC
2. Verify API: `curl http://10.10.10.20:8000/health`
3. Check firewall on Control PC
4. Verify GUI config.py has correct IP

## Maintenance

### Restarting the Service

```bash
sudo systemctl restart drillbot
```

### Updating Drillbot Code

From a development PC with network access to the Pi:

```bash
scp -r app/ config.py drillbotics@<PI_IP>:~/drillbot/
ssh drillbotics@<PI_IP> "sudo systemctl restart drillbot"
```

### Checking Logs

```bash
# Real-time logs
sudo journalctl -u drillbot -f

# Last 100 lines
sudo journalctl -u drillbot -n 100

# Logs since boot
sudo journalctl -u drillbot -b
```

---

## Appendix A: WiFi Configuration (Non-Ideal Solution)

This appendix documents the WiFi-based configuration that was attempted before the Ethernet solution was implemented. This approach is **not recommended** for production use due to the limitations described above.

### Initial WiFi Setup

The Raspberry Pi was initially configured to connect to the university WiFi network (eduroam):

```
Network: eduroam
Protocol: WPA2-Enterprise (EAP-PEAP)
IP Assignment: DHCP (dynamic)
```

### Configuration Files (WiFi-based)

When using WiFi, the configuration required the current dynamic IP:

```python
# config.py - WiFi configuration (NOT RECOMMENDED)
PI_HOST = "10.22.60.77"  # This IP changes!
PI_PORT = 8000
```

### Problems Encountered

1. **IP Address Changes**: The IP address changed each time the Pi reconnected:
   - `10.22.61.40` (first connection)
   - `10.22.61.83` (second connection)
   - `10.22.60.77` (third connection)
   - `10.22.60.223` (fourth connection)

2. **Configuration Drift**: Each IP change required:
   - Determining the new IP (via `hostname -I` on Pi)
   - Updating config files on the Control PC
   - Updating config files in the GUI codebase
   - Restarting services

3. **Operational Fragility**: If the Pi lost WiFi connection (common during drilling operations due to electrical interference), the system became unreachable until manually reconfigured.

### Workarounds Attempted

1. **mDNS/Avahi**: Attempted to use `raspberrypi.local` hostname resolution. Failed due to enterprise network restrictions.

2. **Reserved DHCP**: Requested static IP from NTNU IT. Not available for wireless devices per university policy.

3. **VPN**: Considered but added complexity and introduced additional failure points.

### Conclusion

The WiFi approach required constant manual intervention and was unsuitable for a production drilling control system. The dedicated Ethernet network provides the reliability and determinism required for this safety-critical application.

---

## Appendix B: Hardware Requirements

| Component | Specification | Purpose |
|-----------|--------------|---------|
| Raspberry Pi | Model 4B or 5, 4GB+ RAM | Drillbot server |
| Ethernet Cable | Cat5e or Cat6 | Pi to switch connection |
| Network Switch | Unmanaged, 5+ ports | Rig network backbone |
| Power Supply | 5V 3A USB-C (Pi) | Continuous operation |

## Appendix C: Software Dependencies

### Raspberry Pi

- Raspberry Pi OS (Debian-based)
- Python 3.10+
- Ollama (LLM runtime)
- FastAPI + Uvicorn
- NetworkManager

### Control PC

- Windows 10/11
- Python 3.10+ (for GUI)
- PyQt6 (GUI framework)

---

*Document Version: 1.0*
*Last Updated: May 2026*
*Author: Drillbotics Team*
