from flask import render_template, url_for, flash, session, redirect, request, Blueprint, current_app
from flask_login import login_user, current_user, logout_user, login_required
from esports import db, bcrypt
from esports.models import User, Post
from esports.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm, ResetPasswordForm)
from esports.users.utils import save_picture, send_reset_email
import duo_client
import duo_web

users = Blueprint('users', __name__)

@users.route("/login", methods=['GET', 'POST'])
def login():
    """Login route with Duo authentication."""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # Store the username in the session for Duo verification step
            session['duo_user'] = user.username
            session['remember_me'] = form.remember.data  # Store the "remember me" option
            return redirect(url_for('users.duo_auth'))  # Redirect to Duo authentication

        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('login.html', title='Login', form=form)


@users.route("/duo-auth", methods=['GET', 'POST'])
def duo_auth():
    """Displays the Duo authentication page."""
    username = session.get('duo_user')

    if not username:
        print("❌ ERROR: Session variable `duo_user` is missing! Redirecting to login.")
        return redirect(url_for('users.login'))

    # Ensure `duo_host` is set
    duo_host = current_app.config.get("DUO_HOST")
    if not duo_host:
        raise ValueError("❌ ERROR: `DUO_HOST` is missing in Flask configuration.")
    
    # 🔍 Debug: Check if DUO_AKEY is correctly loaded
    duo_akey = current_app.config.get("DUO_AKEY")
    if not duo_akey:
        raise ValueError("❌ ERROR: `DUO_AKEY` is missing or not loaded!")
    print("🔍 Debug: DUO_AKEY Length:", len(duo_akey))  # Should be 80 characters

    # Generate Duo sign request
    sig_request = duo_web.sign_request(
        current_app.config['DUO_IKEY'],
        current_app.config['DUO_SKEY'],
        current_app.config['DUO_AKEY'],
        username
    )

    # Debug: Log duo_host and sig_request
    print("🔍 Debug: sig_request:", sig_request)
    print("🔍 Debug: Duo Host:", duo_host)

    return render_template('duo_auth.html', sig_request=sig_request, duo_host=duo_host)


@users.route("/duo-auth-verify", methods=['GET', 'POST'])
def duo_auth_verify():
    """Verifies Duo response and completes the login."""
    auth_sig = request.form.get('sig_response')
    username = session.get('duo_user')

    print("🔍 Debug: Received Duo Auth Response:", auth_sig)
    print("🔍 Debug: Username from Session:", username)

    if not auth_sig or not username:
        print("❌ No auth signature or username. Redirecting to login.")
        flash('Duo authentication failed: No response or session expired.', 'danger')
        return redirect(url_for('users.login'))

    # Verify the Duo response
    verified_user = duo_web.verify_response(
        current_app.config['DUO_IKEY'],
        current_app.config['DUO_SKEY'],
        current_app.config['DUO_AKEY'],
        auth_sig
    )

    print("✅ Duo Verified User:", verified_user)

    if not verified_user:
        print("❌ Duo authentication failed. Redirecting to login.")
        flash('Duo authentication failed: Invalid response.', 'danger')
        return redirect(url_for('users.login'))

    if verified_user != username:
        print(f"❌ Mismatch: Expected {username}, but got {verified_user}")
        flash('Duo authentication failed: Username mismatch.', 'danger')
        return redirect(url_for('users.login'))

    # If verification succeeds, log in the user
    user = User.query.filter_by(username=username).first()
    if user:
        print(f"✅ Logging in user: {user.username}")
        login_user(user, remember=session.get('remember_me'))

        # 🚀 Fix: Clear session variables before redirecting
        session.pop('duo_user', None)
        session.pop('remember_me', None)
        session.modified = True  # Ensure session updates are committed

        next_page = session.pop('next', None)
        print("🔀 Redirecting to:", next_page if next_page else url_for('main.home'))

        flash('Login successful!', 'success')
        return redirect(next_page if next_page else url_for('main.home'))

    print("❌ User not found in database. Redirecting to login.")
    flash('Duo authentication successful, but user not found.', 'danger')
    return redirect(url_for('users.login'))



'''
@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)
'''

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
