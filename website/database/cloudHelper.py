# Use this code snippet in your app.
# If you need more information about configurations
# or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developer/language/python/

import json
import os

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv


def create_aws_db_uri() -> str | None:
    try:
        load_dotenv()

        endpoint_name = os.getenv("AWS_DB_ENDPOINT_NAME")
        port_name = os.getenv("AWS_DB_PORT_NAME")
        db_name = os.getenv("AWS_DB_NAME")

        if not endpoint_name or not db_name:
            return None

        secret = get_secret(os.getenv("AWS_SECRET_NAME"), os.getenv("AWS_REGION_NAME"))
        if not secret:
            return None

        secret_dict = json.loads(secret)
        username = secret_dict.get("username")
        password = secret_dict.get("password")

        return f"mysql+mysqlconnector://{username}:{password}@{endpoint_name}/{db_name}"
    except:
        return None


def get_secret(secret_name: str, region_name: str) -> str | None:
    """
    Try get the secret to AWS DB from AWS Secrets Manager\n
    If failed, return None to use local DB
    """
    try:
        secret_name = os.getenv("AWS_SECRET_NAME")
        region_name = os.getenv("AWS_REGION_NAME")
        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )

        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=secret_name
            )
        except ClientError as e:
            # For a list of exceptions thrown, see
            # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
            raise e

        secret = get_secret_value_response['SecretString']
        return secret
    except:
        print("Error retrieving secret from AWS Secrets Manager\nFallbacking to local db...")
        return None