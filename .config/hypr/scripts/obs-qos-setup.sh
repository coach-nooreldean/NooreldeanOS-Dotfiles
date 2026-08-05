#!/bin/bash
# OBS QoS Egress Traffic Shaper
# Run this script with sudo to apply the rules.

if [ "$EUID" -ne 0 ]; then
  echo -e "\033[1;31mPlease run this script with sudo!\033[0m"
  exit 1
fi

# ==============================================================================
# ⚠️ IMPORTANT: SET YOUR UPLOAD SPEED HERE ⚠️
# This MUST be ~90% of your actual Speedtest upload result.
# Examples: "10mbit", "15mbit", "20mbit", "5000kbit"
UPLOAD_SPEED="3200kbit" 
# ==============================================================================

INTERFACE="eno1"

echo -e "\033[1;36m>>> Setting up OBS QoS on $INTERFACE (Max Upload: $UPLOAD_SPEED)...\033[0m"

# 1. Create OBS Group
if ! getent group obs-qos >/dev/null; then
    groupadd obs-qos
    usermod -aG obs-qos nooreldean
    echo "[+] Created group 'obs-qos' and added user nooreldean"
else
    echo "[*] Group 'obs-qos' already exists"
fi

# 2. Clear old TC rules
tc qdisc del dev $INTERFACE root 2>/dev/null
echo "[+] Cleared old traffic rules"

# 3. Setup HTB Root and Classes
# We create a root bucket and direct default traffic to class 20.
tc qdisc add dev $INTERFACE root handle 1: htb default 20

# Root class representing total physical bandwidth allowed
tc class add dev $INTERFACE parent 1: classid 1:1 htb rate $UPLOAD_SPEED ceil $UPLOAD_SPEED

# VIP Class (1:10) -> For OBS. Highest priority (prio 1)
tc class add dev $INTERFACE parent 1:1 classid 1:10 htb rate 2500kbit ceil $UPLOAD_SPEED prio 1

# Default Class (1:20) -> For everything else. Lower priority (prio 2)
tc class add dev $INTERFACE parent 1:1 classid 1:20 htb rate 200kbit ceil $UPLOAD_SPEED prio 2

# Fair Queuing to prevent bufferbloat within the classes
tc qdisc add dev $INTERFACE parent 1:10 handle 10: fq_codel
tc qdisc add dev $INTERFACE parent 1:20 handle 20: fq_codel

# 4. Filter marked packets (Mark = 10) to the VIP Class (1:10)
tc filter add dev $INTERFACE parent 1: protocol ip prio 1 handle 10 fw flowid 1:10
echo "[+] Configured Traffic Control (TC) queues"

# 5. Setup Iptables to mark packets
# Remove old rule if it exists
iptables -t mangle -D OUTPUT -m owner --gid-owner obs-qos -j MARK --set-mark 10 2>/dev/null
# Add new rule: Any traffic originating from a process running under the 'obs-qos' group gets marked with '10'
iptables -t mangle -A OUTPUT -m owner --gid-owner obs-qos -j MARK --set-mark 10
echo "[+] Configured IPTables to tag OBS packets"

echo -e "\033[1;32m>>> QoS Setup Complete! OBS now has maximum upload priority.\033[0m"
