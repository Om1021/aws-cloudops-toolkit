#!/usr/bin/env python3
"""Read-only AWS audit: finds cost waste, security gaps and tagging issues.

Usage:
    python scripts/aws_audit.py --region ap-south-1 [--profile myprofile]
Needs read-only permissions (ec2:Describe*, iam:List*).
"""
import argparse
from datetime import datetime, timezone

import boto3

REQUIRED_TAGS = {"Name", "Owner", "Environment"}
RISKY_PORTS = {22: "SSH", 3389: "RDP"}


def unattached_volumes(ec2):
    vols = ec2.describe_volumes(Filters=[{"Name": "status", "Values": ["available"]}])["Volumes"]
    return [f"{v['VolumeId']} ({v['Size']} GiB)" for v in vols]


def unused_elastic_ips(ec2):
    addrs = ec2.describe_addresses()["Addresses"]
    return [a["PublicIp"] for a in addrs if "AssociationId" not in a]


def stopped_instances(ec2):
    res = ec2.describe_instances(Filters=[{"Name": "instance-state-name", "Values": ["stopped"]}])
    return [i["InstanceId"] for r in res["Reservations"] for i in r["Instances"]]


def untagged_instances(ec2):
    out = []
    for r in ec2.describe_instances()["Reservations"]:
        for i in r["Instances"]:
            keys = {t["Key"] for t in i.get("Tags", [])}
            missing = REQUIRED_TAGS - keys
            if missing:
                out.append(f"{i['InstanceId']} missing {', '.join(sorted(missing))}")
    return out


def open_security_groups(ec2):
    out = []
    for sg in ec2.describe_security_groups()["SecurityGroups"]:
        for rule in sg["IpPermissions"]:
            if not any(r.get("CidrIp") == "0.0.0.0/0" for r in rule.get("IpRanges", [])):
                continue
            lo, hi = rule.get("FromPort", 0), rule.get("ToPort", 65535)
            for port, name in RISKY_PORTS.items():
                if lo <= port <= hi:
                    out.append(f"{sg['GroupId']} ({sg['GroupName']}) allows {name} from 0.0.0.0/0")
    return out


def users_without_mfa(iam):
    out = []
    for page in iam.get_paginator("list_users").paginate():
        for u in page["Users"]:
            if not iam.list_mfa_devices(UserName=u["UserName"])["MFADevices"]:
                out.append(u["UserName"])
    return out


def old_access_keys(iam, max_age_days=90):
    out = []
    now = datetime.now(timezone.utc)
    for page in iam.get_paginator("list_users").paginate():
        for u in page["Users"]:
            for k in iam.list_access_keys(UserName=u["UserName"])["AccessKeyMetadata"]:
                age = (now - k["CreateDate"]).days
                if k["Status"] == "Active" and age > max_age_days:
                    out.append(f"{u['UserName']} key {k['AccessKeyId']} is {age} days old")
    return out


def main():
    p = argparse.ArgumentParser(description="Read-only AWS audit")
    p.add_argument("--region", default="ap-south-1")
    p.add_argument("--profile")
    args = p.parse_args()

    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    ec2, iam = session.client("ec2"), session.client("iam")

    checks = [
        ("COST", "Unattached EBS volumes", unattached_volumes(ec2)),
        ("COST", "Unused Elastic IPs", unused_elastic_ips(ec2)),
        ("COST", "Stopped EC2 instances", stopped_instances(ec2)),
        ("TAGGING", "EC2 instances missing required tags", untagged_instances(ec2)),
        ("SECURITY", "Security groups open to the world on SSH/RDP", open_security_groups(ec2)),
        ("SECURITY", "IAM users without MFA", users_without_mfa(iam)),
        ("SECURITY", "Active access keys older than 90 days", old_access_keys(iam)),
    ]

    print(f"# AWS Audit Report ({args.region}) - {datetime.now():%Y-%m-%d %H:%M}\n")
    total = 0
    for category, title, findings in checks:
        status = "OK" if not findings else f"{len(findings)} found"
        print(f"## [{category}] {title}: {status}")
        for f in findings:
            print(f"  - {f}")
        total += len(findings)
    print(f"\nTotal findings: {total}")


if __name__ == "__main__":
    main()
