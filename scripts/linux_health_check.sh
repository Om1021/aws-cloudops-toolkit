#!/usr/bin/env bash
# Quick Linux server health check (Ubuntu / RHEL). Run: bash scripts/linux_health_check.sh
set -u

echo "=== Host: $(hostname) | $(date '+%F %T') ==="
echo "Uptime / load : $(uptime -p) | $(cut -d' ' -f1-3 /proc/loadavg)"
echo "Memory        : $(free -h | awk '/Mem:/ {print $3 " used of " $2}')"

echo -e "\n--- Disk usage (warn at 80%) ---"
df -hP -x tmpfs -x devtmpfs | awk 'NR==1 {print; next} {use=$5; gsub("%","",use); flag=(use+0>=80)?"  <-- WARNING":""; print $0 flag}'

echo -e "\n--- Top 5 processes by memory ---"
ps -eo pid,comm,%mem,%cpu --sort=-%mem | head -6

echo -e "\n--- Failed systemd services ---"
systemctl --failed --no-legend 2>/dev/null | grep . || echo "None"

echo -e "\n--- Pending package updates ---"
if command -v apt >/dev/null 2>&1; then
  echo "Upgradable packages: $(apt list --upgradable 2>/dev/null | tail -n +2 | wc -l)"
elif command -v dnf >/dev/null 2>&1; then
  echo "Upgradable packages: $(dnf check-update -q 2>/dev/null | grep -c .)"
fi

echo -e "\n--- Listening ports ---"
ss -tulnH 2>/dev/null | awk '{print $1, $5}' | sort -u
