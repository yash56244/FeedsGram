from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, \
    BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, \
    ValidationError, EqualTo
from main.models import User
from flask_wtf.file import FileField, FileAllowed


class LoginForm(FlaskForm):

    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired(),
                           Length(min=4, max=15)])
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
            validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username already exists')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email already exists')


class AccountUpdateForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired(),
                           Length(min=4, max=15)])
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    current_password = PasswordField('Current Password')
    new_password = PasswordField('New Password')
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class EmptyForm(FlaskForm):

    submit = SubmitField('Submit')

class LikeForm(FlaskForm):

    submit = SubmitField('Like')
