'''This file __init__ will tell python this is a package'''

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flaskblog.config import Config

db = SQLAlchemy()                                                                   # Creating an instance so we can make class models for database structure
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'                                                     # 'login' is the function
login_manager.login_message_category = 'info'                                          # info is bootstraps category

mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)                                                          # config file 
    
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    from flaskblog.users.routes import users                                                           # The interpreter goes line by line so it finds the app variable is created
    from flaskblog.posts.routes import posts
    from flaskblog.main.routes import main
    from flaskblog.errors.handlers import errors
    from flaskblog.api.routes import api
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)
    app.register_blueprint(api)
    return app