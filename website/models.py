from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Reviews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    code_id = db.Column(db.String(10), db.ForeignKey('paczkomats.code_id'))
    rating = db.Column(db.Integer)
    review = db.Column(db.String(300))

class Paczkomats(db.Model):
    code_id = db.Column(db.String(10), primary_key=True, autoincrement=False)
    address = db.Column(db.String(200))
    additional_info = db.Column(db.String(500))
    reviews = db.relationship('Reviews')

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    nickname = db.Column(db.String(150))
    notes = db.relationship('Note')
   # notes = db.relationship('Reviews')

