from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Optional, URL
from flask_wtf.file import FileField, FileAllowed

class PlatformForm(FlaskForm):
    device_type = StringField('Device Type', validators=[DataRequired()])
    platform_icon = FileField('Upload Icon (optional)', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Add Platform')

class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')