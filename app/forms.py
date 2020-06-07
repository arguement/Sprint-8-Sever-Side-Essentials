from flask_wtf import FlaskForm

from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import TextField, PasswordField, TextAreaField, DateTimeField , DecimalField

from wtforms.validators import Required, Email, EqualTo, ValidationError, Length, DataRequired

from .custom_validators import check_end_date_greater_than_start

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



class EventForm(FlaskForm):
    """Used to update an existing event"""
    class Meta:
        csrf = False

    title = TextField('Title')
    description = TextAreaField("Description")
    category = TextField('Category')
    start_date = DateTimeField('Start Date')
    end_date = DateTimeField('End Date',validators=[check_end_date_greater_than_start])
    cost = DecimalField(places=2)
    venue = TextField('Venue')
    flyer = TextField('Flyer')
    visibility = TextField('Visibility')

class CreateEventForm(FlaskForm):
    """Used to create an event"""
    class Meta:
        csrf = False

    title = TextField('Title', [Required()])
    description = TextAreaField('Description', [Required()])
    category = TextField('Category', [Required()])
    start_date = DateTimeField('Start Date:', validators=[Required()])
    end_date = DateTimeField('End Date:', validators=[Required(), check_end_date_greater_than_start])
    cost = DecimalField(places=2, validators=[DataRequired()])
    venue = TextField('Venue: ', [Required()])
    flyer = TextField('Flyer: ', [Required()])
    # visibility = BooleanField('Visble: ', validators=[DataRequired(), ])
