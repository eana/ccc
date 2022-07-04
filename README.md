# CircleCI Context Commander

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![CircleCI](https://circleci.com/gh/eana/ccc.svg?style=shield&circle-token=3ba121cc53abe982e955dc61ef1f194c12db063e)](https://app.circleci.com/pipelines/gh/eana/ccc)

<!-- vim-markdown-toc GFM -->

- [Overview](#overview)
- [Setup](#setup)
  - [Install the Dependencies](#install-the-dependencies)
  - [Setup the CircleCI CLI tool](#setup-the-circleci-cli-tool)
- [Configuration](#configuration)
  - [AWS Credentials](#aws-credentials)
  - [AWS IAM Policy](#aws-iam-policy)
  - [Adding a new Circleci context](#adding-a-new-circleci-context)
- [Usage](#usage)

<!-- vim-markdown-toc -->

## Overview

CircleCI Context Commander is a script that is used to rotate the
credentials in a CircleCI context automatically.

## Setup

### Install the Dependencies

This script is written in Python and it's dependencies can be installed using
`pip install -r requirements.txt`.

### Setup the CircleCI CLI tool

This script uses the CircleCI CLI tool to interface with CircleCI, you will
need to install and configure that before you can run the script locally. Full
instructions can be found in the [CircleCI CLI
docs](https://circleci.com/docs/2.0/local-cli/).

## Configuration

### AWS Credentials

You will need to configure access to AWS. Since this script uses the boto3
library you can use your existing `~/.aws` configuration (like the [AWS cli
tool](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html))
or you can set the [AWS Environmental
Variables](https://docs.aws.amazon.com/cli/latest/userguide/cli-environment.html).

**Note - You need to use the `AWS_PROFILE` environmental variables if you are
using switch roles.**

### AWS IAM Policy

When a new context has been created inside Circleci and has an AWS IAM user
with Access/Secret key pair associated with it. The user will require the
following policy `docs/example_policy.json` to be attached so that it will have
the ability to rotate it's own credentials, making sure to change the AWS
Account number inside the user ARN from the Dummy entry.

### Adding a new Circleci context

To add a new circleci context to be automatically rotated you will have to
update the `config.yml` file inside the `.circleci/` folder, this is achieved
by appending another `rotate_keys` job to the cron workflow making sure to pass
the context into the Job, so that the script knows what context to use for
obtaining credentials and rotating them.

## Usage

This script runs on Circleci under the `circleci-context-commander` project but
if you want to run the script locally then the script has a built in help that
lists the full usage.

```bash
python ccc.py --help
```
