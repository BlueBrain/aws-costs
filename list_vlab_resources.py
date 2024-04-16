#!/usr/bin/env python

import boto3
import json
import subprocess
import sys

TAG_KEY = "obp:costcenter:vlabid"
# TAG_KEY = "vlab-id"

# subprocess.check_output(("pip", "install", "awscli"))

# Initialize globally for potential reuse
rg_tagging = boto3.client('resourcegroupstaggingapi')
res_access = boto3.client('ram')
instance_cli = boto3.client("ec2")

cache_buckets = {}


def get_resources(vlab):
    query = {"TagFilters": [{'Key': TAG_KEY, 'Values': [vlab]}]}
    result = rg_tagging.get_resources(PaginationToken='', **query)
    return [r["ResourceARN"] for r in result["ResourceTagMappingList"]]


def get_resources_info(arn_list):
    if not arn_list:
        print("No results:", arn_list, file=sys.stderr)
        return {}

    out_objects = {}
    instance_ids = []
    s3_bucket_ids = []

    for arn in arn_list:
        if arn.startswith("arn:aws:ec2"):
            instance_ids.append(arn[arn.rfind("/")+1:])
        elif arn.startswith("arn:aws:s3"):
            s3_bucket_ids.append(arn.split(":::")[1])

    ATTRS = ["LaunchTime", "InstanceType"]
    instances = instance_cli.describe_instances(InstanceIds=instance_ids)
    instances = instances["Reservations"][0]["Instances"]
    out_objects["instances"] = {
        i["InstanceId"]: {attr: str(i[attr]) for attr in ATTRS}
        for i in instances
    }

    # def get_s3_summary(bucket_id):
    #     bucket_info = {}
    #     # S3 summarize is only availabl in the CLI
    #     info = subprocess.check_output(("aws", "s3", "ls", "--summarize") + (bucket_id,))
    #     for i in info.decode().split("\n"):
    #         if "Total Objects" in i:
    #             bucket_info["total_objects"] = int(i.split(":")[1])
    #         elif "Total Size" in i:
    #             bucket_info["total_size"] = int(i.split(":")[1])
    #     return bucket_info

    # buckets = {}
    # for bucket_id in s3_bucket_ids:
    #     bucket_info = cache_buckets.get(bucket_id) or get_s3_summary(bucket_id)

    #     if bucket_info is None:
    #         bucket_info = get_s3_summary(bucket_id)
    #         cache_buckets[bucket_id] = bucket_info

    #     buckets[bucket_id] = bucket_info

    out_objects["s3_buckets"] = s3_bucket_ids

    return out_objects


def list_handler(event, _context):
    vlab = event.get("vlab")
    if vlab is None and (qstring := event.get("queryStringParameters")):
        vlab = qstring.get("vlab")
    if vlab is None:
        return {"statusCode": 400, "body": "missing vlab query param"}

    result = get_resources(vlab)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(result)
    }


def detail_handler(event, _context):
    vlab = event.get("vlab")
    if vlab is None and (qstring := event.get("queryStringParameters")):
        vlab = qstring.get("vlab")
    if vlab is None:
        return {"statusCode": 400, "body": "missing vlab query param"}

    status_code = 200
    try:
        res = get_resources(vlab)
        result = get_resources_info(res)
    except Exception as e:
        status_code = 400
        result = str(e)

    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(result)
    }


if __name__ == "__main__":
    from pprint import pprint
    if len(sys.argv) < 2:
        raise RuntimeError("Please provide the VLAB is as argument")
    vlab = sys.argv[1]
    resources = get_resources(vlab)
    pprint(get_resources_info(resources))
    pprint(resources)
