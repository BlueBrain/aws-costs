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
to be used with AWS Lambda - notice the `lambda_handler()` function.
It accepts a query parameter `vlab` which we should append to the final url.

To deploy to AWS Lambda get into `deployment` and run terraform. It will package
the executable and create a lambda named `resource_discovery_lambda`

Upon logging in to AWS Console you should find it and you can easily create an http
api gateway for this service. Experiment calling it on the shown url, currently
https://0xe6byl58c.execute-api.us-east-1.amazonaws.com/default/vlab_resource_discovery?vlab=test-vlab1

You should get back a json response along the lines of
```
[
    "arn:aws:s3:::parallelcluster-17763177cd46d13e-v1-do-not-delete"
]
```
Meaning that it found the given S3 bucket as the onlyobject tagged with `test-vlab1`.

## Contributing

Please open Pull Requests.

## License
Blue Brain Project, EPFL 2024
