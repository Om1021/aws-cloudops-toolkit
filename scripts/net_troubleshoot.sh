#!/usr/bin/env bash
# Basic network troubleshooting. Usage: bash scripts/net_troubleshoot.sh <hostname> [port]
HOST="${1:?Usage: $0 <hostname> [port]}"
PORT="${2:-443}"

echo "=== 1. DNS resolution ==="
dig +short "$HOST" 2>/dev/null || nslookup "$HOST"

echo -e "\n=== 2. Reachability (ping x3) ==="
ping -c 3 -W 2 "$HOST" || echo "Ping failed (ICMP may be blocked - check next steps)"

echo -e "\n=== 3. TCP port $PORT ==="
if timeout 5 bash -c "</dev/tcp/$HOST/$PORT" 2>/dev/null; then
  echo "Port $PORT is OPEN"
else
  echo "Port $PORT is CLOSED/FILTERED -> check Security Group, NACL, local firewall"
fi

echo -e "\n=== 4. Route path (traceroute, 10 hops) ==="
traceroute -m 10 -w 2 "$HOST" 2>/dev/null || echo "traceroute not installed"

echo -e "\n=== 5. HTTP timing (if web service) ==="
curl -s -o /dev/null -m 8 -w "DNS: %{time_namelookup}s | Connect: %{time_connect}s | Total: %{time_total}s | Status: %{http_code}\n" "https://$HOST" || echo "HTTP check failed"
