from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from website.database.cloudHelper import get_secret, create_aws_db_uri

LOCAL_DB_NAME = "database.db"


def create_db(db: SQLAlchemy, app: Flask) -> None:
    secret: str = create_aws_db_uri()

    if secret:
        app.config['SQLALCHEMY_DATABASE_URI'] = secret
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{LOCAL_DB_NAME}'

    db.init_app(app)