from flask import Flask, request
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
import os
from dotenv import load_dotenv
from .database.dbFactory import create_db, seed_database
from werkzeug.middleware.proxy_fix import ProxyFix

# Load .env file only if it exists, for local development
if os.path.exists('.env'):
    load_dotenv()

mail = Mail()
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()

SECURITY_HEADERS = {
    "Cache-Control": "no-store, max-age=0",
    "Clear-Site-Data": "\"cache\",\"storage\"",    #,\"cookies\"
    #"Content-Security-Policy": "default-src 'self'; form-action 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'; upgrade-insecure-requests",
    "Cross-Origin-Embedder-Policy": "require-corp",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-origin",
    "Permissions-Policy": "accelerometer=(), autoplay=(), camera=(), cross-origin-isolated=(), display-capture=(), encrypted-media=(), fullscreen=(), geolocation=(), gyroscope=(), keyboard-map=(), magnetometer=(), microphone=(), midi=(), payment=(), picture-in-picture=(), publickey-credentials-get=(), screen-wake-lock=(), sync-xhr=(self), usb=(), web-share=(), xr-spatial-tracking=(), clipboard-read=(), clipboard-write=(), gamepad=(), hid=(), idle-detection=(), interest-cohort=(), serial=(), unload=()",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "X-Content-Type-Options": "nosniff",
    "X-DNS-Prefetch-Control": "off",
    "X-Frame-Options": "deny",
    "X-Permitted-Cross-Domain-Policies": "none",
}

def create_app():
    app = Flask(__name__)
    # Secrets are stored in local .env OR in AWS Beanstalk configuration, os.environ works in both environment
    app.config['SECRET_KEY'] = os.environ.get('APP_SECRET_KEY')
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_ACCOUNT')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

    csrf.init_app(app)

    # If your app runs behind a reverse proxy/load balancer (e.g. nginx, Cloudflare),
    # enable ProxyFix and set the number of proxies in front of your app:
    # app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
    
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
        # MOŻE PRZENIEŚĆ DO SECRETS
        MAIL_SERVER = 'smtp.gmail.com',
        MAIL_PORT = 587,
        MAIL_USE_TLS = True,
    )

    mail.init_app(app)
    migrate.init_app(app, db)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    @app.after_request
    def add_security_headers(response):
        # Add all headers. Send HSTS only if request is secure (HTTPS).
        for name, value in SECURITY_HEADERS.items():
            if name == "Strict-Transport-Security":
                # Only append HSTS on secure requests to avoid forcing HSTS on http dev sites.
                # If you're behind a proxy that terminates TLS, ensure ProxyFix is enabled
                # and the proxy forwards X-Forwarded-Proto so request.is_secure is accurate.
                if request.is_secure:
                    response.headers.setdefault(name, value)
            else:
                # Don't overwrite headers already set by your app unless you want to force them:
                response.headers.setdefault(name, value)
        return response

    @app.route('/health')
    def health_check():
        return 'OK', 200

    return app
