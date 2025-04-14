from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Optional, EqualTo, Email

class PlayerForm(FlaskForm):
    email = StringField("Player Email", validators=[DataRequired(), Email()])
    school = SelectField("School", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Save Player")

class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')

class UploadCSVForm(FlaskForm):
    csv_file = FileField("Upload CSV", validators=[
        FileRequired(),
        FileAllowed(["csv"], "CSV files only!")
    ])
    submit = SubmitField("Upload")