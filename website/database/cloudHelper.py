# Use this code snippet in your app.
# If you need more information about configurations
# or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developer/language/python/

import json
import os


def create_aws_db_uri() -> str | None:
    endpoint_name = os.environ.get("DB_ENDPOINT")
    db_name = os.environ.get("DB_NAME")

    if not endpoint_name or not db_name:
        raise ValueError("Database endpoint or name not set in environment variables.")

    secret = os.environ.get("DB_CREDENTIALS")
    if not secret:
        raise ValueError("Database credentials not set in environment variables.")

    secret_dict = json.loads(secret)
    username = secret_dict.get("username")
    password = secret_dict.get("password")

    return f"mysql+mysqlconnector://{username}:{password}@{endpoint_name}/{db_name}"
