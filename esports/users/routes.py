from flask import render_template, url_for, flash, session, redirect, request, Blueprint, current_app
from flask_login import login_user, current_user, logout_user, login_required
from esports import db, bcrypt
from esports.models import User, Post
from esports.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm, ResetPasswordForm)
from esports.users.utils import save_picture, send_reset_email
from esports.users.duo_utils import send_duo_push_async

users = Blueprint('users', __name__)

@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            txid, message = send_duo_push_async(
                username=user.username,
                ikey=current_app.config['DUO_IKEY'],
                skey=current_app.config['DUO_SKEY'],
                host=current_app.config['DUO_HOST']
            )

            if txid:
                session['duo_txid'] = txid
                session['duo_user'] = user.username
                session['remember_me'] = form.remember.data
                return redirect(url_for('users.duo_waiting'))
            else:
                flash(f'Duo push failed: {message}', 'danger')
                return redirect(url_for('users.login'))

        flash('Login Unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)

@users.route("/duo-waiting")
def duo_waiting():
    if 'duo_txid' not in session or 'duo_user' not in session:
        return redirect(url_for('users.login'))
    return render_template('duo_waiting.html')

@users.route("/duo-status")
def duo_status():
    import duo_client

    txid = session.get('duo_txid')
    username = session.get('duo_user')
    if not txid or not username:
        return {'status': 'error', 'message': 'Missing session data'}, 400

    try:
        auth_client = duo_client.Auth(
            ikey=current_app.config['DUO_IKEY'],
            skey=current_app.config['DUO_SKEY'],
            host=current_app.config['DUO_HOST']
        )

        status = auth_client.auth_status(txid)
        print("🔁 Duo Poll:", status)

        if status.get('waiting', True):
            return {'status': 'waiting'}

        if status.get('success'):
            # Log the user in
            user = User.query.filter_by(username=username).first()
            if user:
                login_user(user, remember=session.get('remember_me'))
                # Clean up session
                session.pop('duo_txid', None)
                session.pop('duo_user', None)
                session.pop('remember_me', None)
                return {'status': 'success'}

        return {'status': 'denied', 'message': status.get('status_msg', 'Denied')}

    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
