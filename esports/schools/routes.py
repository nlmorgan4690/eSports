from flask import render_template, url_for, flash, session, redirect, request, Blueprint, current_app
from flask_login import login_user, current_user, logout_user, login_required
from esports import db, bcrypt
from esports.models import User, Post, Role, School
from esports.schools.forms import SchoolForm

schools = Blueprint('schools', __name__)

@schools.route('/schools')
@login_required
def school_dashboard():
    schools = School.query.all()
    return render_template('schools/dashboard.html', schools=schools)

@schools.route('/schools/<int:school_id>')
@login_required
def view_school(school_id):
    school = School.query.get_or_404(school_id)
    return render_template('schools/view.html', school=school)

@schools.route('/schools/add', methods=['GET', 'POST'])
@login_required
def add_school():
    form = SchoolForm()
    if form.validate_on_submit():
        existing = School.query.filter_by(name=form.name.data.strip()).first()
        if existing:
            flash("A school with that name already exists.", "danger")
        else:
            new_school = School(name=form.name.data.strip(), location=form.location.data.strip())
            db.session.add(new_school)
            db.session.commit()
            flash("School added successfully!", "success")
            return redirect(url_for('schools.school_dashboard'))
    return render_template('schools/form.html', form=form, title="Add School")

@schools.route('/schools/<int:school_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_school(school_id):
    school_obj = School.query.get_or_404(school_id)
    form = SchoolForm()

    if form.validate_on_submit():
        school_obj.name = form.name.data.strip()
        school_obj.location = form.location.data.strip()
        db.session.commit()
        flash("School updated successfully!", "success")
        return redirect(url_for('schools.view_school', school_id=school_obj.id))

    elif request.method == 'GET':
        form.name.data = school_obj.name
        form.location.data = school_obj.location

    return render_template('schools/form.html', form=form, title=f"Edit {school_obj.name}", school=school_obj)
