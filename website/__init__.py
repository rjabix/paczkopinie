import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from .database.dbFactory import create_db, seed_database

mail = Mail()
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    # tymczasowy SECRET_KEY do testów — nie commitować w produkcji
    app.config['SECRET_KEY'] = 'C5hdRK11A1euASHPabKixDI47UARO2ZKgiIQ9vw'
    
    # Make admin check and config available in templates
    from . import config
    app.jinja_env.globals.update(config=config)
    create_db(db, app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Paczkomats, Reviews
    
    with app.app_context():
        db.create_all()
        seed_database(db)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)


    app.config.update(
        # konfiguracja SMTP (w testach wstawiamy wartości bezpośrednio)
        SECRET_KEY = app.config['SECRET_KEY'],
        MAIL_SERVER = 'smtp.gmail.com',
        MAIL_PORT = 587,
        MAIL_USE_TLS = True,
        MAIL_USERNAME = 'paczkopinie@gmail.com',
        MAIL_PASSWORD = 'nxxx nidm degt yniq',
    )

    mail.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
