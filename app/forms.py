from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired,Email,Length


class RegistrationUser(FlaskForm):
    firstname     = StringField('First Name', [Length(min=2, max=30),DataRequired()])
    lastname     = StringField('Last Name', [Length(min=2, max=30),DataRequired()])
    email     = StringField('Email', [Email(),DataRequired()])
    password = StringField('Password', [DataRequired()])
    
    