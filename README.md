# AWS CloudOps Toolkit

Small, read-only toolkit for day-to-day cloud operations support (L1/L2): audit an AWS account for cost, security and tagging issues, check Linux server health, and troubleshoot network connectivity.

## Skills demonstrated

| Area | What the project shows |
|---|---|
| AWS (EC2, VPC, IAM) | Boto3 audit of EBS, Elastic IPs, instances, Security Groups, IAM users and keys |
| Cost optimization | Finds unattached volumes, unused Elastic IPs, stopped instances |
| Security and access | Flags SSH/RDP open to `0.0.0.0/0`, IAM users without MFA, old access keys |
| Linux administration | Health check for CPU, memory, disk, failed services, pending updates (Ubuntu/RHEL) |
| Networking | DNS, ping, TCP port, traceroute and HTTP timing checks; VPC troubleshooting runbook |
| Documentation | Step-by-step L1/L2 runbook for common incidents |

## Project structure

```
aws-cloudops-toolkit/
├── scripts/
│   ├── aws_audit.py            # read-only AWS audit (Python + boto3)
│   ├── linux_health_check.sh   # server health check (Bash)
│   └── net_troubleshoot.sh     # network troubleshooting (Bash)
├── docs/
│   └── troubleshooting-runbook.md
├── requirements.txt
└── README.md
```

## Setup and usage

```bash
pip install -r requirements.txt
aws configure                     # or use --profile

python scripts/aws_audit.py --region ap-south-1
bash scripts/linux_health_check.sh
bash scripts/net_troubleshoot.sh example.com 443
```

## Example audit output

=== Host: Om | 2026-10-24 07:47:20 ===
Uptime / load : up 2 minutes | 0.29 0.19 0.08
Memory        : 491Mi used of 3.7Gi

--- Disk usage (warn at 80%) ---
Filesystem      Size  Used Avail Use% Mounted on
none            1.9G     0  1.9G   0% /usr/lib/modules/6.18.54.1-microsoft-standard-WSL2
/dev/sdb         97M   97M     0 100% /usr/lib/linux-tools/6.18.54.1-microsoft-standard-WSL2  <-- WARNING
drivers         195G  114G   82G  59% /usr/lib/wsl/drivers
/dev/sdd       1007G  1.3G  955G   1% /
none            1.9G     0  1.9G   0% /usr/lib/wsl/lib
rootfs          1.9G  3.4M  1.9G   1% /init
none            1.9G   80K  1.9G   1% /mnt/wslg/versions.txt
none            1.9G   80K  1.9G   1% /mnt/wslg/doc
C:\             195G  114G   82G  59% /mnt/c
D:\              98G   29G   70G  30% /mnt/d
E:\             184G   99G   86G  54% /mnt/e

--- Top 5 processes by memory ---
    PID COMMAND         %MEM %CPU
    294 unattended-upgr  0.8  0.3
    165 networkd-dispat  0.7  0.4
     65 systemd-journal  0.4  0.4
      1 systemd          0.4  1.9
    187 wsl-pro-service  0.3  0.2

--- Failed systemd services ---
None

--- Pending package updates ---
Upgradable packages: 0

--- Listening ports ---
tcp 10.255.255.254:53
tcp 127.0.0.53%lo:53
tcp 127.0.0.54:53
udp 10.255.255.254:53
udp 127.0.0.1:323
udp 127.0.0.53%lo:53
udp 127.0.0.54:53
udp [::1]:323

(Sample format only; output depends on your account.)

## IAM permissions

The audit only reads data. A read-only policy covering `ec2:Describe*`, `iam:ListUsers`, `iam:ListMFADevices` and `iam:ListAccessKeys` is enough. Nothing is created, changed or deleted.

## Ideas to extend

- Add a CloudWatch alarm check (instances with no CPU alarm)
- Export the report to CSV or S3
- Schedule the audit with Lambda and EventBridge
