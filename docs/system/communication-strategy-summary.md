# Drillbot Communication Strategy - Summary

## The Problem

- University WiFi (eduroam) assigns **dynamic IP addresses**
- IP changes on every reconnect (e.g., 10.22.61.40 → 10.22.60.77 → 10.22.60.223)
- NTNU policy: **no static IPs on wireless networks**
- Result: Drillbot became unreachable after each network change

## The Solution

- Use **dedicated Ethernet network** (10.10.10.0/24) via switch
- All devices have **static IPs** configured manually
- Completely **independent from university WiFi**

## Network Setup

| Device | IP Address | Role |
|--------|------------|------|
| Raspberry Pi | 10.10.10.20 | Drillbot API server |
| Control PC | 10.10.10.5 | Operator GUI |
| Trajectory System | 10.10.10.4 | Path planning |

## Why This Works

- **Static**: IPs never change (configured manually, not DHCP)
- **Isolated**: No dependency on university infrastructure
- **Reliable**: Wired connection, <1ms latency
- **Simple**: Just plug in Ethernet cables to switch

## Key Configuration

**Raspberry Pi:**
- NetworkManager connection "drill-link" with static IP
- Systemd service "drillbot" for auto-start on boot

**Control PC:**
- Static IP already configured (no changes needed)
- GUI config points to 10.10.10.20:8000

## Verification

```bash
# From Control PC
ping 10.10.10.20
curl http://10.10.10.20:8000/health
```

## Why Not WiFi (Appendix)

| Issue | Impact |
|-------|--------|
| Dynamic IP | Config files outdated after each reconnect |
| No static IP option | NTNU policy prohibits on wireless |
| Interference | Drilling equipment can disrupt WiFi |
| Latency | 2-10ms vs <1ms wired |

---

*Full technical details: see communication-strategy.md*
