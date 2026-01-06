from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

# Modele bazy danych: Reviews, City, Paczkomats, User
# Recenzje (kto i kiedy ocenił paczkomat)
class Reviews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    code_id = db.Column(db.String(10), db.ForeignKey('paczkomats.code_id'))
    rating = db.Column(db.Integer)
    review = db.Column(db.String(300))
    # Relacja do użytkownika, pozwala dostać obiekt User
    user = db.relationship('User')

# Miasto oraz relacja do paczkomatów
class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    paczkomats = db.relationship('Paczkomats', backref='city', lazy=True)

# Paczkomat (identyfikator i dane)
class Paczkomats(db.Model):
    code_id = db.Column(db.String(10), primary_key=True, autoincrement=False)
    address = db.Column(db.String(200))
    additional_info = db.Column(db.String(500))
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)
    # Recenzje tego paczkomatu
    reviews = db.relationship('Reviews')

# Użytkownik systemu (logowanie i status konta)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    nickname = db.Column(db.String(150))
    # Czy konto potwierdzone e‑mailem
    confirmed = db.Column(db.Boolean, default=False)
    # Relacja do recenzji (opcjonalnie)
    # reviews = db.relationship('Reviews')

