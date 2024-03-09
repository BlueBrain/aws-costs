#!/usr/bin/env sh
set -eu

REGION=us-east-1
if [ $# -ge 1 ]; then
    VLAB_ID=$1
else
    echo "Error: Please provide vlab id. e.g. testing-vlab-123"
    exit 1
fi

aws resourcegroupstaggingapi get-resources \
    --region "$REGION" \
    --tag-filters "Key='vlab-id',Values='$VLAB_ID'" \
    --no-cli-pager \
    --query "ResourceTagMappingList[].ResourceARN"
