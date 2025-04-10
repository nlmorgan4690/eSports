from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField, SelectMultipleField
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from wtforms.validators import DataRequired, Optional, EqualTo, Email
# from wtforms_sqlalchemy.fields import QuerySelectField


class TeamForm(FlaskForm):
    name = StringField("Team Name", validators=[DataRequired()])
    game = SelectField("Game", coerce=int, validators=[DataRequired()])
    school = SelectField("School", coerce=int, validators=[DataRequired()])
    coach = SelectField("Coach", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Create Team")

class EditTeamForm(FlaskForm):
    name = StringField("Team Name", validators=[DataRequired()])
    coach = SelectField("Coach", coerce=int, validators=[DataRequired()])
    game = SelectField("Game", coerce=int, validators=[DataRequired()])
    players = SelectMultipleField("Players", coerce=int)
    submit = SubmitField("Update Team")

class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')
