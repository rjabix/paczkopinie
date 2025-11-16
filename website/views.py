from flask import Blueprint, render_template, request, flash, redirect, jsonify
from flask_login import login_required, current_user
from functools import wraps

from . import db
from .database.repository import Repository
from .models import Reviews, Paczkomats, City
from .config import is_admin
from urllib.parse import quote_plus, unquote_plus


def admin_required(f):
    """Decorator to check if current user is an admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin(current_user):
            flash('Ta funkcja jest dostępna tylko dla administratora.', category='error')
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
@login_required
def home():
    """Show cities as the main page."""
    repository = Repository(current_user, db)
    cities = repository.get_all_cities_with_counts()
    return render_template("home.html", cities=cities)


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

        if not rating or int(rating) == 0:  # jeśli użytkownik nie zaznaczył oceny
            flash('Ocena jest wymagana!', category='error')
        else:
            try:
            
                rating_value = int(rating)
            except ValueError:
                flash('Niepoprawna wartość oceny!', category='error')
                return redirect(request.url)

            # Tworzymy nową opinię z odpowiednią liczbą gwiazdek
            new_review = Reviews(
                user_id=current_user.id,
                code_id=paczkomat_id,
                rating=rating_value,
                review=review
            )

            repository.add_review(new_review)
            flash('Dodano nową opinię o paczkomacie!', category='success')

    reviews = repository.get_reviews_by_paczkomat_code_id(paczkomat_id)
    current_paczkomat = repository.get_paczkomat_by_code_id(paczkomat_id)
    return render_template("paczkomat.html", reviews=reviews, user=current_user, paczkomat=current_paczkomat)


@views.route('/miasto/<city_slug>', methods=['GET'])
@login_required
def miasto(city_slug):
    """Show paczkomats for a selected city."""
    repository = Repository(current_user, db)
    city = repository.get_city_by_slug(city_slug)
    if not city:
        flash('Nie znaleziono takiego miasta!', category='error')
        return redirect('/')

    paczkomats = repository.get_paczkomats_by_city(city.id)
    counts = repository.get_paczkomats_and_number_of_reviews()
    return render_template("miasto.html", city=city, paczkomats=paczkomats, counts=counts)


@views.route('/dodaj_miasto', methods=['POST'])
@login_required
@admin_required
def dodaj_miasto():
    """Add a new city. Admin only."""
    name = request.form.get('name')
    if not name:
        flash('Nazwa miasta jest wymagana!', category='error')
        return redirect('/')

    repository = Repository(current_user, db)
    try:
        repository.add_city(name)
        flash(f'Dodano miasto {name}!', category='success')
    except Exception as e:
        flash(f'Błąd podczas dodawania miasta: {str(e)}', category='error')
    
    return redirect('/')


@views.route('/dodaj_paczkomat', methods=['POST'])
@login_required
@admin_required
def dodaj_paczkomat():
    """Add a new paczkomat. Admin only."""
    code_id = request.form.get('code_id')
    city_id = request.form.get('city_id')
    address = request.form.get('address')
    additional_info = request.form.get('additional_info')

    if not all([code_id, city_id, address]):
        flash('Kod paczkomatu, miasto i adres są wymagane!', category='error')
        return redirect(request.referrer or '/')

    repository = Repository(current_user, db)
    try:
        repository.add_paczkomat(
            code_id=code_id,
            address=address,
            city_id=int(city_id),
            additional_info=additional_info
        )
        flash(f'Dodano paczkomat {code_id}!', category='success')
    except Exception as e:
        flash(f'Błąd podczas dodawania paczkomatu: {str(e)}', category='error')
    
    return redirect(request.referrer or '/')
