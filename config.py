"""Drillbot configuration - single source of truth for network settings."""

# Raspberry Pi network settings
# Static IP on rig Ethernet network (via switch)
# Pi: 10.10.10.10, Control PC: 10.10.10.5, Trajectory: 10.10.10.4
PI_HOST = "10.10.10.20"
PI_PORT = 8000

# API URLs
DRILLBOT_API_BASE = f"http://{PI_HOST}:{PI_PORT}"
DRILLBOT_API_ASK = f"{DRILLBOT_API_BASE}/ask"
DRILLBOT_API_HEALTH = f"{DRILLBOT_API_BASE}/health"
