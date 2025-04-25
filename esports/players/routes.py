import csv
from io import TextIOWrapper
from flask import render_template, url_for, flash, session, redirect, request, Blueprint, current_app
from flask_login import login_user, current_user, logout_user, login_required
from esports import db, bcrypt
from esports.models import Player, School, Game, Team, Role
from esports.players.forms import PlayerForm, DeleteForm, UploadCSVForm
from esports.players.utils import generate_account, sync_player_to_ad, user_exists_in_ad, provision_ad_account, delete_ad_account

import logging

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

        logging.warning(f"Trying to add player: {email} -> {username}")

        if Player.query.filter_by(ad_username=username).first():
            flash(f"A player with the AD username '{username}' already exists.", "danger")
            return redirect(url_for('players.add_player'))

        player = Player(
            name=email,
            school_id=form.school.data,
            ad_username=username,
            ad_passphrase=passphrase
        )
        db.session.add(player)
        db.session.commit()

        if form.sync_to_ad.data:
            try:
                logging.warning(f"Checking if {email} exists in AD...")

                if user_exists_in_ad(username):
                    sync_player_to_ad(player)
                    flash("✅ Player synced to AD group.", "success")
                else:
                    logging.warning(f"{email} not found, provisioning...")

                    provision_ad_account(username, passphrase, hashed)
                    flash("✅ Player provisioned and added to AD group.", "success")
            except Exception as e:
                flash(f"❌ AD Sync/Provision failed: {str(e)}", "danger")
                logging.error(f"Exception syncing/provisioning: {e}")

        flash(f"✅ Player {username} added. Passphrase stored securely.", "success")
        return redirect(url_for('players.players_dashboard'))

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


from esports.players.utils import delete_ad_account

@players.route('/players/<int:player_id>/delete', methods=['POST'])
@login_required
def delete_player(player_id):
    player = Player.query.get_or_404(player_id)

    if current_user.role.role == 'Coach' and player.school_id != current_user.school_id:
        flash("Access denied.", "danger")
        return redirect(url_for('players.players_dashboard'))

    try:
        delete_ad_account(player.ad_username)
        flash(f"🗑️ AD user {player.ad_username} deleted.", "info")
    except Exception as e:
        flash(f"⚠️ Player deleted from app, but AD removal failed: {str(e)}", "warning")

    db.session.delete(player)
    db.session.commit()
    flash("Player deleted from system.", "info")
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
        errors = []

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

            # Add player to database
            player = Player(
                name=email,
                school_id=current_user.school_id,
                ad_username=username,
                ad_passphrase=passphrase
            )
            db.session.add(player)
            db.session.flush()  # Don't fully commit yet, so we can rollback if needed

            # Try to sync/provision AD account
            try:
                if user_exists_in_ad(username):
                    sync_player_to_ad(player)
                else:
                    provision_ad_account(username, passphrase, hashed)
                added += 1

            except Exception as e:
                db.session.rollback()
                skipped.append((email, "AD error"))
                errors.append((email, str(e)))
                continue

        db.session.commit()
        
        flash(f"✅ {added} players added and synced/provisioned. ❌ {len(skipped)} skipped.", "info")

        if skipped:
            for email, reason in skipped:
                flash(f"Skipped {email} — {reason}", "warning")

        if errors:
            for email, err in errors:
                flash(f"Error for {email}: {err}", "danger")

        return redirect(url_for("players.players_dashboard"))

    return render_template("players/upload.html", form=form)



@players.route("/players/<int:player_id>/sync", methods=["POST"])
@login_required
def sync_player(player_id):
    player = Player.query.get_or_404(player_id)

    try:
        if user_exists_in_ad(player.ad_username):
            sync_player_to_ad(player)
            flash(f"✅ {player.name} synced to Active Directory.", "success")
        else:
            # 🧠 Recreate the hashed password from stored plaintext passphrase
            if not player.ad_passphrase:
                flash("❌ Cannot provision — missing stored passphrase.", "danger")
                return redirect(url_for("players.view_player", player_id=player.id))

            passphrase = player.ad_passphrase
            hashed_pass = ('"%s"' % passphrase).encode('utf-16-le')

            provision_ad_account(player.ad_username, passphrase, hashed_pass)
            flash(f"✅ {player.name} provisioned and added to AD.", "success")

        player.ad_synced = True
        db.session.commit()

    except Exception as e:
        player.ad_synced = False
        db.session.commit()
        flash(f"❌ Failed to sync {player.name} to AD: {str(e)}", "danger")

    return redirect(url_for("players.view_player", player_id=player.id))

