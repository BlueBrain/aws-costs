# Aws Costs

## Description

This repo contains several tools to help assessing the costs incurred with AWS.

## Getting started

The tools in this repo generally requires
 - AWS access properly configured
 - Some Python dependencies


With regard to AWS access credentials, please visit
https://docs.aws.amazon.com/cli/latest/userguide/cli-authentication-user.html and follow the most appropriate method for your case.

To meet python dependencies, consider installing them according to the `requirements.txt` file in a new venv, like
```
python -m venv _venv
. _venv/bin/activate
pip install -r requirements.txt
```

## Usage

Tools here are mostly single file. Please run then with the activated python.
```
python costs-ec2.py
```

### list_vlab_resources as AWS Lambda

`list_vlab_resources.py` besides being a Python executable, it is prepared
to be used with AWS Lambda - notice the `*_handler()` functions.
It accepts a query parameter `vlab` which we should append to the final url.

To deploy to AWS Lambda get into `deployment` and run terraform. It will package
the executable and create two lambdas named:
 - `vlab_resource_discovery`
 - `vlab_resource_discovery_detail`

Upon logging in to AWS Console you should find it and you can easily create an http
api gateway for this service. See the [current lambda gateway](https://us-east-1.console.aws.amazon.com/lambda/home?region=us-east-1#/functions/vlab_resource_discovery_detail?tab=configure).

Experiemnt calling at the current endpoint: https://ynqhqsi3ce.execute-api.us-east-1.amazonaws.com/default/vlab_resource_discovery_detail?vlab=test-vlab1



You should get back a json response along the lines of
```
{
    "instances": {
        "i-01d5f75700299a9bd": {
            "LaunchTime": "2024-04-15 15:14:44+00:00",
            "InstanceType": "t3.nano"
        }
    },
    "s3_buckets":{
        "parallelcluster-17763177cd46d13e-v1-do-not-delete": {
            "total_objects": 29,
            "total_size_kb": 833
        }
    }
}
```
Meaning that it found the given objects tagged with `test-vlab1`, and privided some useful info for its incurred costs.

## Contributing

Please open Pull Requests.

# Acknowledgment

The development of this software was supported by funding to the Blue Brain Project,
a research center of the École polytechnique fédérale de Lausanne (EPFL),
from the Swiss government's ETH Board of the Swiss Federal Institutes of Technology.

Copyright (c) 2024 Blue Brain Project - EPFL
