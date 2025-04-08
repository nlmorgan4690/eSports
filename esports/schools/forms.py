from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Optional, EqualTo, Email

class SchoolForm(FlaskForm):
    name = StringField("School Abbreviation", validators=[DataRequired()])
    location = StringField("Address", validators=[DataRequired()])
    submit = SubmitField("Save School")