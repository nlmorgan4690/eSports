from flask import render_template, url_for, flash, session, redirect, request, Blueprint, current_app
from flask_login import login_user, current_user, logout_user, login_required
from esports import db, bcrypt
from esports.models import Player, School, Game, Team, Role
from esports.players.forms import PlayerForm, DeleteForm

players = Blueprint('players', __name__)

@players.route('/players/add', methods=['GET', 'POST'])
@login_required
def add_player():
    form = PlayerForm()

    # Restrict schools for coaches
    if current_user.role.role == 'Coach':
        schools = [(current_user.school_id, current_user.school.name)]
    else:
        schools = [(s.id, s.name) for s in School.query.order_by(School.name).all()]
    form.school.choices = schools

    #  form.game.choices = [(g.id, g.name) for g in Game.query.order_by(Game.name).all()]

    selected_school_id = form.school.data or schools[0][0]
    # form.team.choices = [(0, 'None')] + [(t.id, t.name) for t in Team.query.filter_by(school_id=selected_school_id).order_by(Team.name).all()]

    if form.validate_on_submit():
        player = Player(
            name=form.name.data,
            school_id=form.school.data,
            # game_id=form.game.data,
            # team_id=form.team.data if form.team.data != 0 else None
        )
        db.session.add(player)
        db.session.commit()
        flash("Player added successfully!", "success")
        return redirect(url_for('players.players_dashboard'))

    return render_template("players/form.html", form=form, title="Add Player")

@players.route('/players')
@login_required
def players_dashboard():
    form = PlayerForm()
    delete_form = DeleteForm()
    if current_user.role.role == 'Coach':
        players = Player.query.filter_by(school_id=current_user.school_id).order_by(Player.name).all()
    else:
        players = Player.query.order_by(Player.name).all()
    return render_template('players/dashboard.html', players=players, form=form, delete_form=delete_form)

@players.route('/players/<int:player_id>')
@login_required
def view_player(player_id):
    player = Player.query.get_or_404(player_id)

    # Optional: Coaches can only view their own players
    if current_user.role.role == 'Coach' and player.school_id != current_user.school_id:
        flash("Access denied.", "danger")
        return redirect(url_for('players.players_dashboard'))

    return render_template('players/view.html', player=player)

@players.route('/players/<int:player_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_player(player_id):
    player = Player.query.get_or_404(player_id)

    # Optional: Coaches can only edit their own players
    if current_user.role.role == 'Coach' and player.school_id != current_user.school_id:
        flash("Access denied.", "danger")
        return redirect(url_for('players.players_dashboard'))

    form = PlayerForm()
    delete_form = DeleteForm()

    # Restrict schools for coaches
    if current_user.role.role == 'Coach':
        form.school.choices = [(current_user.school_id, current_user.school.name)]
    else:
        form.school.choices = [(s.id, s.name) for s in School.query.order_by(School.name).all()]

    # form.game.choices = [(g.id, g.name) for g in Game.query.order_by(Game.name).all()]
    # form.team.choices = [(0, 'None')] + [(t.id, t.name) for t in Team.query.filter_by(school_id=player.school_id).order_by(Team.name).all()]

    if form.validate_on_submit():
        player.name = form.name.data
        player.school_id = form.school.data
        # player.game_id = form.game.data
        # player.team_id = form.team.data if form.team.data != 0 else None
        db.session.commit()
        flash("Player updated successfully!", "success")
        return redirect(url_for('players.view_player', player_id=player.id))

    elif request.method == 'GET':
        form.name.data = player.name
        form.school.data = player.school_id
        # form.game.data = player.game_id
        # form.team.data = player.team_id or 0

    return render_template("players/form.html", form=form, delete_form=delete_form, title=f"Edit {player.name}", player=player)


@players.route('/players/<int:player_id>/delete', methods=['POST'])
@login_required
def delete_player(player_id):
    player = Player.query.get_or_404(player_id)

    # Optional: Coaches can only delete their own players
    if current_user.role.role == 'Coach' and player.school_id != current_user.school_id:
        flash("Access denied.", "danger")
        return redirect(url_for('players.players_dashboard'))

    db.session.delete(player)
    db.session.commit()
    flash("Player deleted.", "info")
    return redirect(url_for('players.players_dashboard'))

