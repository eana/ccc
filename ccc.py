#!/usr/bin/env python
import boto3
from boto3.exceptions import Boto3Error
from botocore.exceptions import BotoCoreError
import click

from sh import circleci, ErrorReturnCode


# -- Helper Functions ---------------------------------------------------------
def get_aws_creds(username=None):
    """
    Creates a new AWS key for the AWS user. If there are multiple keys the
    oldest key will be deleted before creating a new key.

    Parameters
    ----------
    username : str
        The AWS username that the created key should be associated with, if not
        set will default to the Current AWS User.

    Returns
    -------
    tuple(str, str)
        Returns a tuple that is contains the AWS KEY ID and the AWS SECRET KEY,
        e.g ('AKxxxxxxxxxxxxxxxxxx','kVxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    """

    if username is None:
        username = boto3.resource("iam").CurrentUser().user_name

    iam = boto3.client("iam")

    # Check how many keys exist and if we have more than one delete the oldest
    # key before creating the new key
    resp = iam.list_access_keys(UserName=username)
    keys = resp.get("AccessKeyMetadata", [])

    if len(keys) > 1:
        keys.sort(key=lambda x: x.get("CreateDate"))
        oldest_key_id = keys[0]["AccessKeyId"]

        click.echo(
            f"Multiple Keys found, deleting the oldest key '{oldest_key_id}'... ",
            nl=False,
        )
        iam.delete_access_key(AccessKeyId=oldest_key_id, UserName=username)
        click.secho("OK", fg="bright_green")

    click.echo("Creating new AWS key... ", nl=False)

    resp = iam.create_access_key(UserName=username)
    key_id = resp["AccessKey"]["AccessKeyId"]
    key_secret = resp["AccessKey"]["SecretAccessKey"]

    click.secho("OK", fg="bright_green")

    return key_id, key_secret


def set_context_env_var(context, name, value):
    """
    Set the Environmental Variable in a given contexts. If the env var already
    exists it will be updated.

    Parameters
    ----------
    context : str
        The CircleCI context that contains the Environmental Variable.
    name : str
        The name of the Environmental Variable to update.
    value : str
        The value the Environmental Variable should be set to.
    """
    click.echo(f"Updating '{name}' in '{context}'... ", nl=False)
    # Delete the existing secret first since the circleci cli tool fails if the
    # secret already exists. If the secret doesn't exist this is a noop and the
    # circleci cli exits with a zero status code as expected.
    circleci("context", "remove-secret", "github", "eana", context, name)
    circleci("context", "store-secret", "github", "eana", context, name, _in=value)
    click.secho("OK", fg="bright_green")


# -- Main CLI -----------------------------------------------------------------
@click.command()
@click.option(
    "--context",
    required=True,
    type=str,
    help="The context that will have it's credentials automatically rotated",
)
@click.option(
    "--username",
    "-u",
    required=False,
    type=str,
    help="The AWS account username. [default: (Current AWS account)]",
)
def main(context, username):
    """
    Rotate the AWS Credentials in a CircleCI context.

    This will generate a new set of AWS credentials and then update the
    Environmental Variables, AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY, in
    the given context.

        CONTEXT - The name of the CircleCI context to update
    """

    click.secho("Checking CircleCI CLI tool is setup... ", nl=False)
    try:
        circleci("diagnostic")
    except ErrorReturnCode as e:
        click.secho("ERROR", fg="bright_red")
        raise click.ClickException(
            f"The circleci cli tool is not setup correctly, unable to continue! {e}"
        )
    click.secho("OK", fg="bright_green")
    click.secho(f"Current Context is: '{context}'", fg="bright_green")
    try:
        new_key_id, new_key_secret = get_aws_creds(username)
    except (Boto3Error, BotoCoreError) as e:
        click.secho("ERROR", fg="bright_red")
        raise click.ClickException(f"Unable to create a new AWS key: {e}")

    try:
        set_context_env_var(context, "AWS_ACCESS_KEY_ID", new_key_id)
        set_context_env_var(context, "AWS_SECRET_ACCESS_KEY", new_key_secret)
    except ErrorReturnCode as e:
        click.secho("ERROR", fg="bright_red")
        raise click.ClickException(f"Unable to update the context: {e}")

    click.secho("All done!", fg="bright_green")


if __name__ == "__main__":
    main()
