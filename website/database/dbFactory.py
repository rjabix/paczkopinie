import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from website.database.cloudHelper import create_aws_db_uri

LOCAL_DB_NAME = "database.db"

def create_db(db: SQLAlchemy, app: Flask) -> None:
    env = os.environ.get("ENVIRONMENT")
    if env == "Production":
        app.config['SQLALCHEMY_DATABASE_URI'] = create_aws_db_uri()
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{LOCAL_DB_NAME}'
    db.init_app(app)

# Fill in Paczkomats to database and fill empty city_id of Paczkomats records
def seed_database(db: SQLAlchemy) -> None:
    from website.models import Paczkomats, City

    existing_paczkomats = Paczkomats.query.all()
    if existing_paczkomats and not hasattr(Paczkomats, 'city_id'):
        # Temporary tables
        db.session.execute('''
            CREATE TABLE IF NOT EXISTS paczkomats_temp (
                code_id VARCHAR(10) PRIMARY KEY,
                address VARCHAR(200),
                additional_info VARCHAR(500),
                city_id INTEGER NOT NULL,
                FOREIGN KEY(city_id) REFERENCES city(id)
            )
        ''')
        db.session.execute('''
            CREATE TABLE IF NOT EXISTS city (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) UNIQUE NOT NULL,
                slug VARCHAR(100) UNIQUE NOT NULL
            )
        ''')

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