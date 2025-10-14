from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        rating = request.form.get('rating')
        review = request.form.get('review')
        # Dodać potem code_id z paczkomatów do opinii tutaj i w obiekcie Reviews !
        if len(rating) < 1:
            flash('Ocena jest wymagana!', category='error')
        else:
            new_review = Reviews(id=current_user.id, rating=rating, review=review)  #providing the schema for the note
            db.session.add(new_review) #adding the note to the database
            db.session.commit()
            flash('Dodano nową opinię o paczkomacie!', category='success')

    return render_template("home.html", user=current_user)


# do przemyslenia i przerobienia - usuwanie opini
@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id: # to musi być - będzie można usuwać tylko swoje opinie
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
