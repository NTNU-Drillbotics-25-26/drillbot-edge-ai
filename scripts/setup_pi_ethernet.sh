#!/bin/bash
# Setup Pi as Ethernet gateway with DHCP server for direct PC connection
# Run on Pi: sudo ./setup_pi_ethernet.sh
#
# After running this script:
# - Pi will have static IP 192.168.50.1 on eth0
# - Pi will assign IPs (192.168.50.10-50) to connected devices via DHCP
# - Control PC just needs to plug in Cat6 cable (no config changes needed)

set -e

PI_IP="192.168.50.1"
DHCP_RANGE_START="192.168.50.10"
DHCP_RANGE_END="192.168.50.50"
NETMASK="255.255.255.0"

echo "============================================"
echo "  Drillbot Pi Ethernet Setup"
echo "  Pi IP: $PI_IP"
echo "  DHCP range: $DHCP_RANGE_START - $DHCP_RANGE_END"
echo "============================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root: sudo $0"
    exit 1
fi

# Install dnsmasq if not present
if ! command -v dnsmasq &> /dev/null; then
    echo "Installing dnsmasq..."
    apt-get update
    apt-get install -y dnsmasq
fi

# Stop dnsmasq while configuring
systemctl stop dnsmasq 2>/dev/null || true

# Configure static IP on eth0
echo "Configuring static IP on eth0..."

if [ -f /etc/dhcpcd.conf ]; then
    # Raspberry Pi OS uses dhcpcd

    # Backup existing config
    cp /etc/dhcpcd.conf /etc/dhcpcd.conf.backup.$(date +%Y%m%d_%H%M%S)

    # Remove existing eth0 config if present
    sed -i '/# Drillbot Ethernet/,/^$/d' /etc/dhcpcd.conf
    sed -i '/interface eth0/,/^interface\|^$/d' /etc/dhcpcd.conf

    # Add static IP config for eth0
    cat >> /etc/dhcpcd.conf << EOF

# Drillbot Ethernet - Static IP for direct connection
interface eth0
static ip_address=$PI_IP/24
nogateway
nolink
EOF

    echo "dhcpcd configured for eth0"

elif command -v nmcli &> /dev/null; then
    # NetworkManager (Ubuntu, etc.)
    nmcli con delete "drillbot-eth" 2>/dev/null || true
    nmcli con add type ethernet con-name "drillbot-eth" ifname eth0 \
        ipv4.addresses "$PI_IP/24" \
        ipv4.method manual \
        connection.autoconnect yes
    echo "NetworkManager configured for eth0"
fi

# Configure dnsmasq as DHCP server on eth0 only
echo "Configuring dnsmasq DHCP server..."

cat > /etc/dnsmasq.d/drillbot-ethernet.conf << EOF
# Drillbot Ethernet DHCP Server
# Only serve DHCP on eth0 (direct cable connection)

interface=eth0
bind-interfaces

# DHCP range for connected PCs
dhcp-range=$DHCP_RANGE_START,$DHCP_RANGE_END,$NETMASK,24h

# Don't act as DNS server (use upstream)
port=0

# Log DHCP leases
log-dhcp
EOF

# Disable dnsmasq on other interfaces
echo "except-interface=wlan0" >> /etc/dnsmasq.d/drillbot-ethernet.conf

# Enable and start services
echo "Starting services..."

systemctl restart dhcpcd 2>/dev/null || true
systemctl enable dnsmasq
systemctl start dnsmasq

# Apply IP immediately
ip addr flush dev eth0 2>/dev/null || true
ip addr add $PI_IP/24 dev eth0 2>/dev/null || true
ip link set eth0 up

echo ""
echo "============================================"
echo "  Setup Complete!"
echo "============================================"
echo ""
echo "Pi Ethernet IP: $PI_IP"
echo "DHCP range: $DHCP_RANGE_START - $DHCP_RANGE_END"
echo ""
echo "Verify with:"
echo "  ip addr show eth0"
echo "  systemctl status dnsmasq"
echo ""
echo "Connect Cat6 cable to control PC and test:"
echo "  - PC will auto-receive IP via DHCP"
echo "  - From PC: ping $PI_IP"
echo "  - From PC: curl http://$PI_IP:8000/health"
echo ""
