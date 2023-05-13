#!/bin/bash

apt update -y
sleep 10
apt install socat -y

interface="eth0"

ip_address=$(ip addr show dev "$interface" | awk '/inet / {gsub(/\/.*/, "", $2); print $2; exit}' | head -1)
echo "$ip_address"
cmd="socat tcp-listen:8443,reuseaddr,fork,bind=$ip_address tcp:127.0.0.1:4567"
sleep 10
nohup bash -c "$cmd" >/dev/null 2>&1 &
