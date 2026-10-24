# Troubleshooting Runbook (L1/L2)

## Scenario 1: Cannot SSH / connect to an EC2 instance
1. Check instance state and status checks (2/2 passed?).
2. Security Group: inbound rule for the port from the client IP.
3. NACL: allow inbound and outbound ephemeral ports (1024-65535).
4. Route table: public subnet has `0.0.0.0/0` to an Internet Gateway.
5. Instance has a public IP / Elastic IP.
6. VPC Flow Logs: look for `REJECT` entries for the source IP.
7. Inside the OS: `ss -tulpn`, `systemctl status sshd`, local firewall.

## Scenario 2: Private instance has no internet access
1. Private subnet route table: `0.0.0.0/0` to a NAT Gateway.
2. NAT Gateway sits in a public subnet with an Elastic IP.
3. Check outbound Security Group / NACL rules.
4. Check DNS: `dig amazon.com`; VPC has DNS resolution enabled.

## Scenario 3: High CPU / memory alert
1. Review CloudWatch metrics (CPU, StatusCheckFailed).
2. Run `bash scripts/linux_health_check.sh` for top processes and disk.
3. Check logs (`journalctl -xe`) and restart the service if safe.
4. Document root cause and fix in the ticket; rightsize if it recurs.

## Scenario 4: Unexpected cost increase
1. Run `python scripts/aws_audit.py` for orphaned volumes, idle EIPs, stopped instances.
2. Review NAT Gateway data processing and cross-AZ traffic.
3. Enforce tagging (Name, Owner, Environment) to identify owners.
