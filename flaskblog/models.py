from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer                 # Making token for password reset
from flaskblog import db, login_manager
from flask import current_app
from flask_login import UserMixin                                                      # User class inherts from UserMixin

@login_manager.user_loader                                                             # The session will be handled by the flask extension so we dont have to code it
def load_user(user_id):
    return User.query.get(int(user_id))                                                # This will fetch the user id from database and return the data of the specified user

class User(db.Model, UserMixin):                                                       # Each class is table in database. The classes are called models which are represent like a table 
    id = db.Column(db.Integer, primary_key=True)                                       # Creating columns in the table
    username = db.Column(db.String(12), unique=True, nullable=False)                   # nullable means that it doesn't remain empty
    email = db.Column(db.String(120), unique=True, nullable=False)
    gravatar_url = db.Column(db.String(120))
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')       # Arguments in SQLAlchmey
    password = db.Column(db.String(60), nullable=False)

    # Creating One to Many Relation
    posts = db.relationship('Post', backref='author', lazy=True)                       # The post attribute has a relationship with Post() model or class. The backref lets us create a new column and get the author                    
                                                                                       # who created the post. The lazy argument just defines when sqlalchemy loads the data from the database
    
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)                           # generating token for password reset
        return s.dumps({'user_id':self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):                                  # verifying user if its them or not
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
            user_id = data.get('user_id')  # Extract the user_id from the decoded data
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)     # No parenthesis for datetime.utcnow because we want the function not the current time
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"