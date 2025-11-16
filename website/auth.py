from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, mail
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature


auth = Blueprint('auth', __name__)

def _get_serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])


def send_confirmation_email(user_email):
    ts = _get_serializer()
    token = ts.dumps(user_email, salt='email-confirm-salt')
    confirm_url = url_for('auth.confirm_email', token=token, _external=True)
    subject = "Potwierdź konto - Paczkopinie"
    body = f"Kliknij w link aby potwierdzić konto:\n\n{confirm_url}\n\nJeśli nie zakładałeś konta, zignoruj tę wiadomość."
    msg = Message(subject=subject, recipients=[user_email], body=body, sender=current_app.config.get('MAIL_USERNAME'))
    mail.send(msg)



@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user: User = User.query.filter_by(email=email).first()
        if user:
            if not user.confirmed:
                flash('Konto nie zostało potwierdzone. Sprawdź e‑mail lub wyślij ponownie potwierdzenie.', category='error')
                return redirect(url_for('auth.resend_confirmation'))
            if user.password == password:
                flash('Zalogowano pomyślnie!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Błędny email lub hasło!', category='error')
        else:
            flash('Błędny email lub hasło!', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        nickname = request.form.get('nickName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Błędne dane', category='error')
        elif len(email) < 6:
            flash('Adres e-mail musi być dłuższy niż 5 znaków', category='error')
        elif len(nickname) < 3:
            flash('Nick musi być dłuższy niż 2 znaki.', category='error')
        elif password1 != password2:
            flash('Hasła nie są identyczne.', category='error')
        elif len(password1) < 10:
            flash('Hasło musi zawierać co najmniej 10 znaków.', category='error')
        else:
            new_user = User(email=email, nickname=nickname, password=password1, confirmed=False)
            db.session.add(new_user)
            db.session.commit()
            try:
                send_confirmation_email(email)
                flash('Konto utworzone. Sprawdź e‑mail, aby aktywować konto.', category='success')
                return render_template('post_sign_up.html', user=current_user)
            except Exception:
                flash('Konto utworzone, ale nie udało się wysłać e‑maila. Skontaktuj się z administratorem.', category='error')
                return redirect(url_for('auth.login'))
    return render_template("sign_up.html", user=current_user)


@auth.route('/confirm/<token>')
def confirm_email(token):
    ts = _get_serializer()
    try:
        email = ts.loads(token, salt='email-confirm-salt', max_age=60*60*24)  # 24h
    except SignatureExpired:
        flash('Link wygasł. Poproś o ponowne wysłanie potwierdzenia.', category='error')
        return redirect(url_for('auth.resend_confirmation'))
    except BadSignature:
        flash('Nieprawidłowy link potwierdzający.', category='error')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('Konto już zostało potwierdzone.', category='info')
    else:
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        flash('Konto potwierdzone. Możesz się zalogować.', category='success')
    return redirect(url_for('auth.login'))


@auth.route('/resend-confirmation', methods=['GET', 'POST'])
def resend_confirmation():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user and not user.confirmed:
            try:
                send_confirmation_email(email)
                flash('Wysłano ponownie e‑mail potwierdzający.', category='success')
            except Exception:
                flash('Błąd przy wysyłce e‑maila.', category='error')
        # else:
        #     flash('Brak niepotwierdzonego konta o podanym e‑mailu.', category='error')
        # return redirect(url_for('auth.login'))
    return render_template('resend_confirmation.html', user=current_user)