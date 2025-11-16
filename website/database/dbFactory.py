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
    
    with app.app_context():
        # Import models so they are known to SQLAlchemy
        from website.models import User, Reviews, City, Paczkomats
        
        # Create tables if they don't exist
        db.create_all()

def seed_database(db: SQLAlchemy) -> None:
    from website.models import Paczkomats, City

    # First, check if we need to migrate existing data
    existing_paczkomats = Paczkomats.query.all()
    if existing_paczkomats and not hasattr(Paczkomats, 'city_id'):
        # Create a temporary table
        db.session.execute('''
            CREATE TABLE IF NOT EXISTS paczkomats_temp (
                code_id VARCHAR(10) PRIMARY KEY,
                address VARCHAR(200),
                additional_info VARCHAR(500),
                city_id INTEGER NOT NULL,
                FOREIGN KEY(city_id) REFERENCES city(id)
            )
        ''')
        
        # Create the city table if it doesn't exist
        db.session.execute('''
            CREATE TABLE IF NOT EXISTS city (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) UNIQUE NOT NULL,
                slug VARCHAR(100) UNIQUE NOT NULL
            )
        ''')

    # Add sample data if the database is empty
    if City.query.first() is None:
        wroclaw = City(name='Wrocław', slug='wroclaw')
        db.session.add(wroclaw)
        db.session.commit()

        if Paczkomats.query.first() is None:
            sample_paczkomats = [
                Paczkomats(
                    code_id='WE123',
                    address='Wrocław, Wybrzeże Wyspiańskiego 27',
                    city_id=wroclaw.id
                ),
                Paczkomats(
                    code_id='WR-2505',
                    address='Wrocław, Kościuszki 15',
                    city_id=wroclaw.id
                ),
                Paczkomats(
                    code_id='WJN-39',
                    address='Wrocław, Jedności Narodowej 39',
                    city_id=wroclaw.id
                ),
            ]
            db.session.bulk_save_objects(sample_paczkomats)
            db.session.commit()