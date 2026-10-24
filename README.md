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

```
# AWS Audit Report (ap-south-1) - 2026-10-24 10:30

## [COST] Unattached EBS volumes: 2 found
  - vol-0abc123 (20 GiB)
## [SECURITY] Security groups open to the world on SSH/RDP: 1 found
  - sg-0def456 (default-ssh) allows SSH from 0.0.0.0/0
## [SECURITY] IAM users without MFA: OK
```

(Sample format only; output depends on your account.)

## IAM permissions

The audit only reads data. A read-only policy covering `ec2:Describe*`, `iam:ListUsers`, `iam:ListMFADevices` and `iam:ListAccessKeys` is enough. Nothing is created, changed or deleted.

## Ideas to extend

- Add a CloudWatch alarm check (instances with no CPU alarm)
- Export the report to CSV or S3
- Schedule the audit with Lambda and EventBridge
