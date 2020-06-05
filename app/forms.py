from flask_wtf import FlaskForm

from wtforms import TextField, PasswordField, TextAreaField, DateTimeField

from wtforms.validators import Required, Email, EqualTo, ValidationError, Length

class RegistrationForm(FlaskForm):
    class Meta:
        csrf = False

    firstname = TextField('Firstname', [Required()])
    lastname = TextField('Lastname', [Required()])
    email = TextField('Email', [Required(), Email()])
    password = PasswordField('Password', [Required()])
    # confirm = PasswordField('Confirm Password', [Required(), EqualTo('password', message='Passwords must match!')])

class RegFrontEndForm(RegistrationForm):
    confirm = PasswordField('Confirm Password', [Required(), EqualTo('password', message='Passwords must match!')])

class LoginForm(FlaskForm):
    class Meta:
        csrf = False

    email = TextField('Email', [Required(), Email()])
    password = PasswordField('Password', [Required()])
