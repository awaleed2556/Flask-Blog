'''This folder called users is package and this file is a blueprint so is the post and main folders'''

from flask import render_template, url_for, flash, redirect, request, Blueprint
from flaskblog import  db, bcrypt
from flaskblog.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm, 
                             ResetPasswordForm, RequestResetForm)                                 # Importing classes from our forms file    
from flaskblog.models import User, Post                                                  # 'flaskblog.' is the package name(The folder we made)
from flask_login import login_user, current_user, logout_user, login_required                           # This extension will help handling login, logout sessions
from flaskblog.users.utils import save_picture, send_reset_email, gravatarImage

users = Blueprint('users', __name__)

pfpLink = None

@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():                                                                               # condition if the form of registration is filled
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')                    # Hashing the password
        pfpLink = gravatarImage(form.email.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, gravatar_url=pfpLink)               # Using the User class from models file      
        db.session.add(user)                                                                                    # sqlalchemy's method to add the user object in database
        db.session.commit()
        flash(f'Account created!👳🏽‍♂️', 'success')                                                                 # flash is flask func and takes two args.'success' is bootstrap's category
        return redirect(url_for('users.login'))
    return render_template('register.html',title='Create An Account', form=form)

@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()                                             # Instantiating the object
        if user and bcrypt.check_password_hash(user.password, form.password.data):                             # Checking the email and password exists in database
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccssful. Please check again and fuck you', 'danger')
    return render_template('login.html',title='Log In', form=form)

@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data

        db.session.commit()
        flash('Account Updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename='profile_pics/'+ current_user.image_file)      # This holds the profile picture. "current_user.image_file" is the file uploaded by user
    return render_template('account.html',title='My Account', image_file=image_file, form=form)

@users.route('/user/<string:username>')                                                                                             # same route leads to the same home page
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
            .order_by(Post.date_posted.desc())\
            .paginate(page=page, per_page=7)                                  # paginate is sqlalchemy's method
    return render_template('user_posts.html',posts=posts, user=user)

@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent for the password reset', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@users.route('/reset_token/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Verification Expired. Please try again', 'warning')
        return redirect(url_for('users..reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():                                                                              # Updating the passowrd     # condition if the form of registration is filled
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')                    # Hashing the password
        user.password = hashed_password
        db.session.commit()
        flash(f'Passoword Updated!🚔', 'success')                                                                 # flash is flask func and takes two args.'success' is bootstrap's category
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)