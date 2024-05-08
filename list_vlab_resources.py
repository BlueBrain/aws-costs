#!/usr/bin/env python

import boto3
import json
import sys

VLAB_TAG_KEY = "obp:costcenter:vlabid"
PROJECT_TAG_KEY = "obp:costcenter:project"

# Initialize globally for potential reuse
rg_tagging = boto3.client('resourcegroupstaggingapi')
res_access = boto3.client('ram')
instance_cli = boto3.client("ec2")
s3_client = boto3.client('s3')

cache_buckets = {}


class InvalidRequest(Exception):
    """When the request is invalid, likely due to invalid or missing data"""


def get_resources(vlab, project=None):
    if project is not None:
        query = {"TagFilters": [{'Key': PROJECT_TAG_KEY, 'Values': [vlab]}]}
    else:
        query = {"TagFilters": [{'Key': VLAB_TAG_KEY, 'Values': [vlab]}]}
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
            instance_ids.append(arn[arn.rfind("/") + 1:])
        elif arn.startswith("arn:aws:s3"):
            s3_bucket_ids.append(arn.split(":::")[1])

    ATTRS = ["LaunchTime", "InstanceType"]
    instances = instance_cli.describe_instances(InstanceIds=instance_ids)
    instances = instances["Reservations"][0]["Instances"]
    out_objects["instances"] = {
        i["InstanceId"]: {attr: str(i[attr]) for attr in ATTRS}
        for i in instances
    }

    buckets = {}
    for bucket_id in s3_bucket_ids:
        if (bucket_info := cache_buckets.get(bucket_id)) is None:
            bucket_info = cache_buckets[bucket_id] = get_s3_summary(bucket_id)
        buckets[bucket_id] = bucket_info

    out_objects["s3_buckets"] = buckets

    return out_objects


def get_s3_summary(bucket_id):
    """Get the summary of an s3 bucket total usage
    """
    total_objects = 0
    total_size = 0
    response = s3_client.list_objects_v2(Bucket=bucket_id)

    for object in response['Contents']:
        if (size := object['Size']) > 0:
            total_objects += 1
            total_size += size

    return {"total_objects": total_objects, "total_size_kb": total_size // 1024}


def list_handler(event, _context):
    try:
        vlab, project, _opts = _get_vlab_query_params(event)
        result = get_resources(vlab, project)
    except InvalidRequest as e:
        return response_text(str(e), code=400)
    except Exception as e:
        return response_text(str(e), code=500)

    return response_json(result)


def detail_handler(event, _context):
    try:
        vlab, project, _opts = _get_vlab_query_params(event)
        resources = get_resources(vlab, project)
        result = get_resources_info(resources)
    except InvalidRequest as e:
        return response_text(str(e), code=400)
    except Exception as e:
        return response_text(str(e), code=500)

    return response_json(result)


def _get_vlab_query_params(event):
    vlab_id = event.get("vlab_id")
    options = {}

    if vlab_id is None and "queryStringParameters" in event:
        if options := event.get("queryStringParameters"):
            vlab_id = options.pop("vlab", None)

    project_id = options.pop("project", None)

    if vlab_id is None and project_id is None:
        raise InvalidRequest("missing required 'vlab' or 'project' query param")

    return vlab_id, project_id, options


def response_text(text: str, code: int = 200):
    return {"statusCode": code, "body": text}


def response_json(data, code: int = 200):
    return {
        "statusCode": code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(data),
    }


if __name__ == "__main__":
    from pprint import pprint
    if len(sys.argv) < 2:
        raise RuntimeError("Please provide the VLAB is as argument")
    vlab = sys.argv[1]
    resources = get_resources(vlab)
    pprint(get_resources_info(resources))
    pprint(resources)
