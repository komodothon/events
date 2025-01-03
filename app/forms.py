from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, TextAreaField, SubmitField, DateTimeLocalField
from wtforms.validators import DataRequired, EqualTo

class RegisterForm(FlaskForm):
    username = StringField('Username: ', validators=[DataRequired()])
    email = EmailField('Email: ', validators=[DataRequired()])
    password = PasswordField('Password: ', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password: ', validators=[DataRequired(), EqualTo('password', message='passwords must match')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username: ', validators=[DataRequired()])
    password = PasswordField('Password: ', validators=[DataRequired()])
    submit = SubmitField('Login')

class CreateEventForm(FlaskForm):
    title = StringField('Title: ', validators=[DataRequired()])
    date = DateTimeLocalField("Date: ", format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    location = StringField('Location: ', validators=[DataRequired()])
    description = TextAreaField('Description: ', validators=[DataRequired()])
    submit = SubmitField('Create Event')