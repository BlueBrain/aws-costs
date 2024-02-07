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

## Contributing

Please open Pull Requests.

## License
Blue Brain Project, EPFL 2024
