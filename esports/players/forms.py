from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Optional, EqualTo, Email

class PlayerForm(FlaskForm):
    name = StringField("Player Name", validators=[DataRequired()])
    school = SelectField("School", coerce=int, validators=[DataRequired()])
    game = SelectField("Game", coerce=int, validators=[DataRequired()])
    team = SelectField("Team (optional)", coerce=int, choices=[(0, 'None')])
    submit = SubmitField("Save Player")

class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')