import csv
from io import TextIOWrapper
from flask import render_template, url_for, flash, session, redirect, request, Blueprint, current_app
from flask_login import login_user, current_user, logout_user, login_required
from esports import db, bcrypt
from esports.models import Player, School, Game, Team, Role
from esports.players.forms import PlayerForm, DeleteForm, UploadCSVForm
from esports.players.utils import generate_account

players = Blueprint('players', __name__)

@players.route('/players/add', methods=['GET', 'POST'])
@login_required
def add_player():
    form = PlayerForm()

    # Restrict school choices based on user role
    if current_user.role.role == 'Coach':
        schools = [(current_user.school_id, current_user.school.name)]
    else:
        schools = [(s.id, s.name) for s in School.query.order_by(School.name).all()]
    form.school.choices = schools

    if form.validate_on_submit():
        email = form.email.data
        username, passphrase, hashed = generate_account(email)

        # ✅ Check for duplicate AD username
        if Player.query.filter_by(ad_username=username).first():
            flash(f"A player with the AD username '{username}' already exists.", "danger")
            return redirect(url_for('players.add_player'))

        player = Player(
            name=email,  # still storing email in 'name'
            school_id=form.school.data,
            ad_username=username,
            ad_passphrase=passphrase
        )

        db.session.add(player)
        db.session.commit()

        flash(f"Player {username} added. Passphrase stored securely.", "success")
        return redirect(url_for('players.view_players'))  # Adjust if needed

    return render_template("players/form.html", form=form, title="Add Player")


@players.route('/players')
@login_required
def players_dashboard():
    selected_school_id = request.args.get("school_id", type=int)
    form = DeleteForm()

    if current_user.role.role == "Coach":
        players = Player.query.filter_by(school_id=current_user.school_id).order_by(Player.name).all()
        schools = []  # not shown to coaches
    else:
        schools = School.query.order_by(School.name).all()
        if selected_school_id:
            players = Player.query.filter_by(school_id=selected_school_id).order_by(Player.name).all()
        else:
            players = Player.query.order_by(Player.name).all()

    return render_template("players/dashboard.html", players=players, schools=schools, selected_school_id=selected_school_id, form=form)

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
        player.name = form.email.data
        player.school_id = form.school.data
        # player.game_id = form.game.data
        # player.team_id = form.team.data if form.team.data != 0 else None
        db.session.commit()
        flash("Player updated successfully!", "success")
        return redirect(url_for('players.view_player', player_id=player.id))

    elif request.method == 'GET':
        form.email.data = player.name
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

@players.route("/players/upload", methods=["GET", "POST"])
@login_required
def upload_players():
    if current_user.role.role != "Coach":
        flash("Only coaches can upload CSVs.", "danger")
        return redirect(url_for("players.players_dashboard"))
    
    form = UploadCSVForm()

    if form.validate_on_submit():
        file = form.csv_file.data
        stream = TextIOWrapper(file, encoding="utf-8")
        reader = csv.reader(stream)

        added = 0
        skipped = []

        for row in reader:
            if not row:
                continue

            email = row[0].strip().lower()

            # Validate email format
            if "@" not in email or "." not in email:
                skipped.append((email, "Invalid email"))
                continue

            # Check for duplicates
            if Player.query.filter_by(name=email).first():
                skipped.append((email, "Already exists"))
                continue

            # Generate credentials
            username, passphrase, hashed = generate_account(email)

            # Check for duplicate username (rare edge case)
            if Player.query.filter_by(ad_username=username).first():
                skipped.append((email, "Username exists"))
                continue

            # Add player
            player = Player(
                name=email,
                school_id=current_user.school_id,
                ad_username=username,
                ad_passphrase=passphrase
            )
            db.session.add(player)
            added += 1

        db.session.commit()
        flash(f"✅ {added} players added. ❌ {len(skipped)} skipped.", "info")

        if skipped:
            for email, reason in skipped:
                flash(f"Skipped {email} — {reason}", "warning")

        return redirect(url_for("players.players_dashboard"))

    return render_template("players/upload.html", form=form)