from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField , PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length , Email, EqualTo, ValidationError
from flaskblog.models import User

# This class inherits from FlaskForm which is imported above
class RegistrationForm(FlaskForm):
    # username and email,etc are Fields
    username = StringField('Username',                                        # DataRequired means can't be empty
                           validators=[DataRequired(), Length(min=3, max=8)]) # thus we dont need to write this from scratch
    
    email = StringField('Email', 
                        validators=[DataRequired(), Email()])
    
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',                     # Notice we wrote the variable name in EqualTo()
                                     validators=[DataRequired(), EqualTo('password')])
    
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is taken')
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email already exists')

# Creating A login Form
class LoginForm(FlaskForm):
    email = StringField('Email', 
                        validators=[DataRequired(), Email()])
    
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')

# Update Account info form
class UpdateAccountForm(FlaskForm):
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=3, max=8)]) 
    
    email = StringField('Email', 
                        validators=[DataRequired(), Email()])
    
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','png'])])

    submit = SubmitField('Update')

    def validate_username(self, username):                                  # Checks for username or email already exists
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('This username is taken')
        
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('This email already exists')
            
# Form for 'Forgot Password' 
class RequestResetForm(FlaskForm):
    email = StringField('Email', 
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Reset',validators=[DataRequired()])

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('This email does not exists')
        
# New Password confirming form
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',                     # Notice we wrote the variable name in EqualTo()
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Confirm',validators=[DataRequired()]) 