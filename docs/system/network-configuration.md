---
id: network-configuration
title: Network configuration
aliases:
  - network settings
  - udp port
  - tcp port
  - what port does the gui use
  - how does the gui connect to the rig
  - network configuration
  - communication settings
screen: null
component: system
raw_tags:
  - UDP
  - TCP
  - NetworkConfiguration
  - Port5005
  - Port4050
  - Port4051
  - Port4052
status: confirmed_on_current_rig
source_type: specification
historic: false
---

# Network Configuration

The system uses direct Ethernet connection between the Control PC and Raspberry Pi for reliable, static communication.

## Rig Ethernet Network (10.10.10.x)

| Device | IP Address | Interface |
|--------|------------|-----------|
| Raspberry Pi (Drillbot) | 10.10.10.20 | eth0 |
| Control PC | 10.10.10.5 | Ethernet |
| Trajectory System | 10.10.10.4 | Ethernet |

**Setup:**
- All devices connected via switch
- Pi uses NetworkManager connection "drill-link" with static IP

**Drillbot API:**
- Base URL: `http://10.10.10.20:8000`
- Health check: `curl http://10.10.10.20:8000/health`

---

The GUI uses UDP and TCP for communication with the rig and trajectory system.

## UDP Telemetry (Incoming)

| Setting | Value |
|---------|-------|
| Host | 0.0.0.0 (all interfaces) |
| Port | 5005 |
| Buffer | 4096 bytes |
| Timeout | 1.0 second |
| Format | JSON or CSV key=value |

**Purpose:** Receives real-time drilling data from the low-level computer.

## TCP Trajectory Receiver (Incoming)

| Setting | Value |
|---------|-------|
| Port | 4050 |
| Protocol | Binary with header |

**Message types:**
- Type 0: Dubins curve (planned path)
- Type 1: Generic vector
- Type 2: Target waypoints

**Purpose:** Receives planned trajectory from the trajectory planning system.

## TCP Run Config (Outgoing)

| Setting | Value |
|---------|-------|
| Host | localhost (configurable) |
| Port | 4051 |

**Purpose:** Sends run configuration to the control system.

## TCP Trajectory (Outgoing)

| Setting | Value |
|---------|-------|
| Host | 10.10.10.4 (configurable) |
| Port | 4052 |

**Purpose:** Sends target points to the trajectory planning system.

## Common Issues

**No data received:**
1. Check UDP port 5005 is not blocked by firewall
2. Verify the low-level computer is sending data
3. Check network connectivity

**Trajectory not showing:**
1. Verify TCP port 4050 is accessible
2. Check trajectory system is running
