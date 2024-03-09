#!/usr/bin/env python

import boto3
import pprint
import sys
client = boto3.client('resourcegroupstaggingapi')

TAG_KEY="vlab-id"
try:
    vlab=sys.argv[1]
except IndexError:
    raise RuntimeError("Please provide the VLAB is as argument")

result = client.get_resources(
    PaginationToken='',
    TagFilters=[
        {'Key': TAG_KEY, 'Values': [vlab]},
    ],
)

resources = [r["ResourceARN"] for r in result["ResourceTagMappingList"]]
pprint.pprint(resources)
