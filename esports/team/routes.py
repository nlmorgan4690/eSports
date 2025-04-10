from flask import render_template, url_for, flash, session, redirect, request, Blueprint, current_app
from flask_login import login_user, current_user, logout_user, login_required
from esports import db, bcrypt
from esports.models import User, Post, Role, Team, PlayerTeam, School, Game, Player
from esports.team.forms import (TeamForm, DeleteForm, EditTeamForm)

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



@team.route("/teams/<int:team_id>/edit", methods=["GET", "POST"])
@login_required
def edit_team(team_id):
    team = Team.query.get_or_404(team_id)
    form = EditTeamForm()

    # Dynamically limit coaches to users with the coach role
    coach_role = Role.query.filter_by(role="Coach").first()
    form.coach.choices = [(u.id, u.username) for u in User.query.filter_by(role_id=coach_role.id).all()]
    # Load game choices
    form.game.choices = [(g.id, g.name) for g in Game.query.order_by(Game.name).all()]


    # Only allow players from the same school who aren't already on a team
    eligible_players = Player.query.filter_by(school_id=team.school_id).all()
    form.players.choices = [(p.id, p.name) for p in eligible_players]

    if request.method == "GET":
        form.name.data = team.name
        form.coach.data = team.coach_id
        form.game.data = team.game_id  # 👈 pre-populate game
        form.players.data = [pt.player_id for pt in team.players]


    if form.validate_on_submit():
        team.name = form.name.data
        team.coach_id = form.coach.data
        team.game_id = form.game.data  # 👈 save selected game

        # Clear and reset players
        PlayerTeam.query.filter_by(team_id=team.id).delete()
        selected_player_ids = form.players.data

        # Enforce max team size
        max_team_size = team.game.max_team_size
        if len(selected_player_ids) > max_team_size:
            flash(f"Cannot assign more than {max_team_size} players to this team.", "danger")
            return redirect(url_for("team.edit_team", team_id=team.id))

        for player_id in selected_player_ids:
            db.session.add(PlayerTeam(player_id=player_id, team_id=team.id))

        db.session.commit()
        flash("Team updated successfully.", "success")
        return redirect(url_for("team.team_dashboard"))

    return render_template("teams/edit_team.html", form=form, team=team, max_team_size=team.game.max_team_size)


@team.route('/teams/<int:team_id>/delete', methods=['POST'])
@login_required
def delete_team(team_id):
    team = Team.query.get_or_404(team_id)
    db.session.delete(team)
    db.session.commit()
    flash("Team deleted successfully!", "success")
    return redirect(url_for('team.team_dashboard'))
