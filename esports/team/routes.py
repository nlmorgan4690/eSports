from flask import render_template, url_for, flash, session, redirect, request, Blueprint, current_app
from flask_login import login_user, current_user, logout_user, login_required
from esports import db, bcrypt
from esports.models import User, Post, Role, Team, PlayerTeam, School, Game
from esports.team.forms import (TeamForm, DeleteForm)

team = Blueprint('team', __name__)

@team.route('/teams', methods=['GET', 'POST'])
@login_required
def team_dashboard():
    teams = Team.query.all()
    form = DeleteForm()
    return render_template('team_dashboard.html', teams=teams, form=form)

@team.route('/teams/<int:team_id>')
@login_required
def view_team(team_id):
    team = Team.query.get_or_404(team_id)
    form = DeleteForm()
    return render_template('team_detail.html', team=team, form=form)

@team.route('/teams/add', methods=['GET', 'POST'])
@login_required
def add_team():
    form = TeamForm()

    # Load choices
    form.game.choices = [(g.id, g.name) for g in Game.query.order_by(Game.name).all()]
    form.school.choices = [(s.id, s.name) for s in School.query.order_by(School.name).all()]
    
    coach_role = Role.query.filter_by(role='Coach').first()
    if coach_role:
        form.coach.choices = [(u.id, u.username) for u in User.query.filter_by(role_id=coach_role.id).order_by(User.username).all()]
    else:
        form.coach.choices = []

    if form.validate_on_submit():
        existing = Team.query.filter_by(name=form.name.data.strip()).first()
        if existing:
            flash("Team already exists.", "danger")
        else:
            team = Team(
                name=form.name.data.strip(),
                game_id=form.game.data,
                school_id=form.school.data,
                coach_id=form.coach.data
            )
            db.session.add(team)
            db.session.commit()
            flash("Team added successfully!", "success")
            return redirect(url_for('team.team_dashboard'))

    return render_template("add_team.html", form=form)



@team.route('/teams/<int:team_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_team(team_id):
    team = Team.query.get_or_404(team_id)
    form = TeamForm()

    if form.validate_on_submit():
        # Optional: check if the name is being changed to an existing team
        existing = Team.query.filter(Team.name == form.name.data.strip(), Team.id != team.id).first()
        if existing:
            flash("Another team with that name already exists.", "danger")
        else:
            team.name = form.name.data.strip()
            team.school = form.school.data.strip()
            team.coach = form.coach.data.strip()
            db.session.commit()
            flash("Team updated successfully!", "success")
            return redirect(url_for('team.view_team', team_id=team.id))
    elif request.method == 'GET':
        # Pre-fill form with current values
        form.name.data = team.name
        form.school.data = team.school
        form.coach.data = team.coach

    return render_template("edit_team.html", form=form, team=team)

@team.route('/teams/<int:team_id>/delete', methods=['POST'])
@login_required
def delete_team(team_id):
    team = Team.query.get_or_404(team_id)
    db.session.delete(team)
    db.session.commit()
    flash("Team deleted successfully!", "success")
    return redirect(url_for('team.team_dashboard'))
