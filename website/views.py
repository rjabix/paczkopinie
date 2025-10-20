from flask import Blueprint, render_template, request, flash, redirect
from flask_login import login_required, current_user
from flask import jsonify

from . import db
from .database.repository import Repository
from .models import Reviews

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    repository = Repository(current_user, db)

    paczkomats = repository.get_paczkomats_and_number_of_reviews()
    return render_template("home.html", paczkomats=paczkomats)


@views.route('/delete_review/<int:review_id>', methods=['GET'])
@login_required
def delete_review(review_id):
    repository = Repository(current_user, db)
    repository.delete_review(review_id)
    flash('Opinia usunięta!', category='success')
    return redirect(request.referrer or '/')


@views.route('/paczkomat/<paczkomat_id>', methods=['GET', 'POST'])
@login_required
def paczkomat(paczkomat_id):
    repository = Repository(current_user, db)

    if request.method == 'POST':
        rating = request.form.get('rating')
        review = request.form.get('review')

        if not rating:  # jeśli użytkownik nie zaznaczył oceny
            flash('Ocena jest wymagana!', category='error')
        else:
            try:
            
                rating_value = int(rating)
                stars = "⭐" * rating_value
            except ValueError:
                flash('Niepoprawna wartość oceny!', category='error')
                return redirect(request.url)

            # Tworzymy nową opinię z odpowiednią liczbą gwiazdek
            new_review = Reviews(
                user_id=current_user.id,
                code_id=paczkomat_id,
                rating=stars,
                review=review
            )

            repository.add_review(new_review)
            flash('Dodano nową opinię o paczkomacie!', category='success')

    reviews = repository.get_reviews_by_paczkomat_code_id(paczkomat_id)
    return render_template("paczkomat.html", reviews=reviews, user=current_user)