from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Reviews, Paczkomats
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        rating = request.form.get('rating')
        review = request.form.get('review')
        # Dodać potem code_id na podstawie wyszukanego paczkomatu tutaj i w obiekcie Reviews !
        if len(rating) < 1:
            flash('Ocena jest wymagana!', category='error')
        else:
            new_review = Reviews(user_id=current_user.id, code_id='WE123', rating=rating, review=review)
            db.session.add(new_review)
            db.session.commit()
            flash('Dodano nową opinię o paczkomacie!', category='success')
    # DO TESTOWANIA USUNĄĆ database.db bo code_id musi być unique
    # test_record = Paczkomats(code_id='WE123', address='Paczkowa', additional_info='jazz')
    # db.session.add(test_record)
    # test_record2 = Reviews(user_id=1, code_id='WE123', rating=5, review='polecam K.H.')
    # db.session.add(test_record2)
    # db.session.commit()
    # Tu należy wyciągnąć dane tylko wyszukiwanego paczkomatu
    return render_template("home.html", paczkomats='WE123')


# # do przemyslenia i przerobienia - usuwanie opini
# @views.route('/delete-note', methods=['POST'])
# def delete_note():
#     note = json.loads(request.data) # this function expects a JSON from the INDEX.js file
#     noteId = note['noteId']
#     note = Note.query.get(noteId)
#     if note:
#         if note.user_id == current_user.id: # to musi być - będzie można usuwać tylko swoje opinie
#             db.session.delete(note)
#             db.session.commit()
#
#     return jsonify({})
