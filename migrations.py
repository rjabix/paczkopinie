from flask_migrate import Migrate
from website import create_app, db

app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    with app.app_context():
        # Import models so they are known to Flask-Migrate
        from website.models import User, Reviews, Paczkomats, City
        
        # Create tables for models (only if they don't exist)
        db.create_all()