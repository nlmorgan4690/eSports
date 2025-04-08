from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from esports import db
from esports.models import Game
from esports.games.forms import GamesForm, DeleteForm  # adjust import path if needed
from PIL import Image, UnidentifiedImageError

games = Blueprint('games', __name__)

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from esports import db
from esports.models import Game
from esports.games.forms import GamesForm
from esports.games.utils import save_game_icon

games = Blueprint('games', __name__)

@games.route('/games')
@login_required
def games_dashboard():
    games_list = Game.query.order_by(Game.name).all()
    return render_template('games/dashboard.html', games=games_list)


@games.route('/games/<int:game_id>')
@login_required
def view_game(game_id):
    game = Game.query.get_or_404(game_id)
    form = DeleteForm()
    return render_template('games/view.html', game=game, form=form)


@games.route('/games/add', methods=['GET', 'POST'])
@login_required
def add_game():
    form = GamesForm()
    if form.validate_on_submit():
        filename = None
        if form.game_icon.data:
            filename = save_game_icon(form.game_icon.data)

        new_game = Game(
            name=form.name.data.strip(),
            max_team_size=form.max_team_size.data,
            game_icon=filename or "default.png"
        )
        db.session.add(new_game)
        db.session.commit()
        flash("Game added successfully!", "success")
        return redirect(url_for('games.games_dashboard'))

    return render_template('games/form.html', form=form, title="Add New Game")


@games.route('/games/<int:game_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_game(game_id):
    game = Game.query.get_or_404(game_id)
    form = GamesForm()
    form.original_game = game

    if form.validate_on_submit():
        try:
            new_icon = save_game_icon(form.game_icon.data)
            if new_icon:
                game.game_icon = new_icon
        except ValueError:
            flash("Failed to process uploaded image. Please upload a valid image file.", "danger")
            return render_template('games/form.html', form=form, title=f"Edit {game.name}", game=game)


        game.name = form.name.data.strip()
        game.max_team_size = form.max_team_size.data
        db.session.commit()
        flash("Game updated successfully!", "success")
        return redirect(url_for('games.view_game', game_id=game.id))

    elif request.method == 'GET':
        form.name.data = game.name
        form.max_team_size.data = game.max_team_size

    return render_template('games/form.html', form=form, title=f"Edit {game.name}")

@games.route('/games/<int:game_id>/delete', methods=['POST'])
@login_required
def delete_game(game_id):
    game = Game.query.get_or_404(game_id)
    db.session.delete(game)
    db.session.commit()
    flash("Game deleted successfully!", "success")
    return redirect(url_for('games.games_dashboard'))