from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Optional, EqualTo, Email, Length, MacAddress, Regexp

class DeviceForm(FlaskForm):
    device_name = StringField("Device Name", validators=[DataRequired()])
    device_mac = StringField("MAC Address", validators=[
        DataRequired(),
        Regexp(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', message="Invalid MAC address")
    ])
    platform = SelectField("Platform", coerce=int, validators=[DataRequired()])
    school = SelectField("School", coerce=int)  # Will be optional unless admin
    submit = SubmitField("Register Device")


class UploadDeviceCSVForm(FlaskForm):
    csv_file = FileField("Upload CSV", validators=[
        FileRequired(),
        FileAllowed(["csv"], "CSV files only!")
    ])
    submit = SubmitField("Upload")