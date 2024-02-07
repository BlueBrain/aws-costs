#!/usr/bin/env python
import boto3
import json
from collections import defaultdict
from datetime import datetime, timezone

AWS_REGION = "us-east-1"

ec2 = boto3.resource("ec2")
pricing = boto3.client("pricing")


def get_ec2_usage_hours():
    usage_hours_per_type = defaultdict(float)  # [instance_type-> hours]
    for instance in ec2.instances.all():
        usage = datetime.now(timezone.utc) - instance.launch_time
        usage_hours_per_type[instance.instance_type] += round(usage.total_seconds() / 3600, 1)

    return usage_hours_per_type


def get_ec2_hourly_price(instance_type):
    plist = pricing.get_products(
        ServiceCode="AmazonEC2",
        Filters=[
            {"Type": "TERM_MATCH", "Field": "regionCode", "Value": AWS_REGION},
            {"Type": "TERM_MATCH", "Field": "instanceType", "Value": instance_type},
            {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": "Linux"},
            {"Type": "TERM_MATCH", "Field": "tenancy", "Value": "Shared"},
            {"Type": "TERM_MATCH", "Field": "preInstalledSw", "Value": "NA"},
            {"Type": "TERM_MATCH", "Field": "capacitystatus", "Value": "Used"},
            {"Type": "TERM_MATCH", "Field": "termType", "Value": "OnDemand"},
        ],
        MaxResults=10,
    )
    assert plist["PriceList"]
    product_price_list = json.loads(plist["PriceList"][0])["terms"]["OnDemand"]
    assert product_price_list
    product_price = next(iter(next(iter(product_price_list.values()))["priceDimensions"].values()))
    return float(product_price["pricePerUnit"]["USD"])


if __name__ == "__main__":
    total_cost = 0
    cur_usage = get_ec2_usage_hours()

    print("Cost breakdown:")
    for instance_type, hours in cur_usage.items():
        price_h = get_ec2_hourly_price(instance_type)
        price_line = hours * price_h
        print(f" * {instance_type}: {hours}h x {price_h:.3f} . . . . . . . $ {price_line:.2f} ")
        total_cost += price_line

    print(f"\nTOTAL: {total_cost:.2f} USD")
