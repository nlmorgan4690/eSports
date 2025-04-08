from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Optional, EqualTo, NumberRange, ValidationError
from esports.models import Game

class GamesForm(FlaskForm):
    name = StringField("Game Name", validators=[DataRequired()])
    max_team_size = IntegerField("Max Team Size", validators=[DataRequired(), NumberRange(min=1, max=100)])
    game_icon = FileField('Game Icon', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField("Save Game")

    def validate_name(self, name):
        existing_game = Game.query.filter_by(name=name.data.strip()).first()
        if existing_game and (not hasattr(self, 'original_game') or existing_game.id != self.original_game.id):
            raise ValidationError("A game with this name already exists.")

class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')