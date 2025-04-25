from flask import render_template, url_for, flash, session, redirect, request, Blueprint, current_app
from flask_login import login_user, current_user, logout_user, login_required
from esports import db, bcrypt
from esports.models import User, Post, Role, School
from esports.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm, ResetPasswordForm, DeleteForm,
                                   ChangePasswordForm)
from esports.users.utils import save_picture, send_reset_email
from esports.users.duo_utils import send_duo_push_async

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated and current_user.role.role != "Admin":
        return redirect(url_for('main.home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        role_obj = Role.query.get(form.role.data)
        school_id = form.school.data if role_obj.role == "Coach" else None

        if role_obj.role == "Coach" and (not school_id or school_id == 0):
            flash('You must select a school for a coach.', 'danger')
            return render_template('register.html', title='Register', form=form)

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=hashed_password,
                    role_id=form.role.data,
                    school_id=school_id)
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

@users.route("/user_dashboard")
@login_required
def user_dashboard():
    users = User.query.order_by(User.email).all()
    form = DeleteForm()
    return render_template('user_dashboard.html', users=users, form=form)

@users.route("/user/<int:user_id>/delete", methods=['POST'])
@login_required
def delete_user (user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f"User '{user.username}' deleted.", "success")
    return redirect(url_for("users.user_dashboard"))



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

@users.route("/user/<int:user_id>/view")
@login_required
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template("users/view_user.html", user=user)

@users.route("/account/change_password", methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, form.current_password.data):
            new_hash = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            current_user.password = new_hash
            db.session.commit()
            flash('Your password has been updated.', 'success')
            return redirect(url_for('users.account'))
        else:
            flash('Incorrect current password.', 'danger')
    return render_template('users/change_password.html', form=form)

@users.route("/user/<int:user_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = RegistrationForm()  # <-- No obj=user here

    # Populate original values for uniqueness validation
    form._original_username = user.username
    form._original_email = user.email

    form.role.choices = [(r.id, r.role) for r in Role.query.order_by(Role.role).all()]
    form.school.choices = [(0, 'Select a School')] + [(s.id, s.name) for s in School.query.order_by(School.name).all()]

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role_id = form.role.data

        school_val = int(form.school.data)
        user.school_id = school_val if school_val != 0 else None

        if form.password.data:
            user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        db.session.commit()
        flash('User updated successfully.', 'success')
        return redirect(url_for('users.user_dashboard'))

    else:
        print("🚫 Form errors:", form.errors)

    # Prepopulate only safe fields
    form.username.data = user.username
    form.email.data = user.email
    form.role.data = user.role_id
    form.school.data = user.school_id or 0
    form.password.data = ''
    form.confirm_password.data = ''

    return render_template('users/edit_user.html', form=form, user=user)
