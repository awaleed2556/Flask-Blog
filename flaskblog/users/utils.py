import os
import secrets
from flask import url_for, current_app
from flask_mail import Message
from PIL import Image                                                                    # this package will help resize the image
from flaskblog import mail
from libgravatar import Gravatar

def save_picture(form_picture):                                 # Func for picture
    random_hex = secrets.token_hex(8)                           # random hex for picture
    _,f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    
    output_size = (125,125)                                    # setting a value for the image to be resized to
    i = Image.open(form_picture)                               # setting i to the method
    i.thumbnail(output_size)                                   # Resizing the image
    i.save(picture_path)                                        # saving the resized picture to path

    return picture_fn

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com',recipients=[user.email])
    msg.body = f'''To Reset your Password, click the link below:
{url_for('users.reset_token',token=token,_external=True)}

If you did not request to change the password, Ignore this email and no changes will be made.'''
    mail.send(msg)


# Grabbing email's profile pic
def gravatarImage(email):
    avatar = Gravatar(email)
    return avatar.get_image()
