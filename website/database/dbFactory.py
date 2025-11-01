import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from website.database.cloudHelper import create_aws_db_uri

LOCAL_DB_NAME = "database.db"


def create_db(db: SQLAlchemy, app: Flask) -> None:
    env: str = None
    try:
        if os.environ.get("ENVIRONMENT") == "DEV":
            env = "DEV"
    finally:
        env = "Local" if env is None else "DEV"

    print("Current Environment:", env)
    if env == "DEV":
        app.config['SQLALCHEMY_DATABASE_URI'] = create_aws_db_uri()
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{LOCAL_DB_NAME}'

    db.init_app(app)

def seed_database(db: SQLAlchemy) -> None:
    from website.models import Paczkomats

    if Paczkomats.query.first() is None:
        sample_paczkomats = [
            Paczkomats(code_id='WE123', address='Wrocław, Wybrzeże Wyspiańskiego 27'),
            Paczkomats(code_id='WR-2505', address='Wrocław, Kościuszki 15'),
            Paczkomats(code_id='WJN-39', address='Wrocław, Jedności Narodowej 39'),
        ]
        db.session.bulk_save_objects(sample_paczkomats)
        db.session.commit()