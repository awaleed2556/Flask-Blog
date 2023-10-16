from flask import Blueprint, request, make_response,g
from flaskblog.models import User, Post
from flaskblog import db,bcrypt
from flaskblog.config import Config
from flaskblog.users.utils import gravatarImage
from sqlalchemy.exc import IntegrityError
import json, jwt, datetime
from functools import wraps

api = Blueprint('api', __name__)

# Decoding the token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        authorization_header = request.headers.get('Authorization')

        if not authorization_header:
            return json.dumps({'message': 'Token is missing'})

        # Splitting the header into parts
        parts = authorization_header.split()

        # For the user to write Bearer with every token he sends
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return json.dumps({'message': 'Token is invalid'})

        token = parts[1]                                                             # Getting the token from the list which is parsed authorization_header

        # For every exception raised by the jwt.decode
        try:
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])        # Decoding, assuming "Bearer" is used
            g.current_user = data
        except jwt.ExpiredSignatureError:
            return json.dumps({'message': 'Token has expired'})
        except jwt.InvalidTokenError:
            return json.dumps({'message': 'Token is invalid'})
        return f(*args, **kwargs)

    return decorated

def update_post(post_id):
    if not request.json:
        return json.dumps({'message':'JSON data is missing.'}), 400
    
    if "title" not in request.json or "content" not in request.json:
        return json.dumps({'message':'Enter correct title and content'}), 400
    
    if not request.json['title'] or not request.json['content']:
        return json.dumps({'message':'Title or content cannot be empty.'}), 400
    
    post = Post.query.get_or_404(post_id)
    if post.author.username != g.current_user['username']:
        return json.dumps({'message':'Forbidden, You are not allowed to do that!'}), 403
    post.title = request.json['title']
    post.content = request.json['content']
    db.session.commit()

    
    return json.dumps({"message":'Post Updated!','post':current_post(post)}, indent=4, sort_keys=False, default=str), 202

def current_post(post):
    post_data = {
        "id":post.id,
        "title":post.title,
        "content":post.content,
        "author": post.author.username,
        "date posted": post.date_posted
    }
    return post_data

def all_posts(posts):
    output = []
    for post in posts:
        post_data = {
            "id": post.id,
            "title": post.title,
            "date posted": post.date_posted,
            "content": post.content,
            "author": post.author.username
        }
        output.append(post_data)
    return output

def all_users(users):
    output = []
    for user in users:
        user_data = {'id':user.id, 
                    'username':user.username,
                    'email':user.email}
        output.append(user_data)
    return output

# Request every user data
@api.route('/api/userdata')
@api.route('/api/userdata/<int:id>')
def UserID(id=None):
    if id:
        users = User.query.get_or_404(id)
        return json.dumps({'id':users.id, 'username':users.username, 'email':users.email}), 200
    
    users = User.query.all()
    
    return json.dumps({"Users":all_users(users)}), 200
        
# Request every post made
@api.route('/api/postdata')
@api.route('/api/postdata/<int:id>')
def PostID(id=None):
    if id:
        post = Post.query.get_or_404(id)
        return json.dumps({"id":post.id, "title":post.title, "date posted":post.date_posted, "content":post.content, "author":post.author.username}, indent=4, sort_keys=False, default=str), 200

    posts = Post.query.all()
    return json.dumps({'Posts': all_posts(posts)}, indent=4, sort_keys=False, default=str), 200
        
# Registering a new user
@api.route('/api/register', methods=['POST'])
def registerUser():
    try :
        if 'username' not in request.json or 'email' not in request.json or 'password' not in request.json:
            return json.dumps({"message": "Enter correct username, email, and password."}), 400
        
        if not request.json['email'] or not request.json['username'] or not request.json['password']:
            return json.dumps({"message":"Please enter username, email and password correctly."}), 400
        
        hashed_password = bcrypt.generate_password_hash(request.json['password']).decode('utf-8')
        pfpLink = gravatarImage(request.json['email'])
        user = User(username=request.json['username'], email=request.json['email'], password=hashed_password, gravatar_url=pfpLink)
        db.session.add(user)
        db.session.commit()
        return json.dumps({'message':'Fuck You'}),201
    except IntegrityError as e:
        return json.dumps({"message":"Username or Email already exists."}), 400
    except Exception:
        return json.dumps({"message":"An error occured on registration."}), 500
    

# Login and this returns a jwt
@api.route('/api/login', methods=['POST'])
def loginUser():
    if not request.json:
        return json.dumps({'message':'JSON data is missing.'}), 400 
    
    if 'email' not in request.json or 'password' not in request.json:
        return json.dumps({'message':'Enter email and password'}), 400
    
    if not request.json['email'] or not request.json['password']:
        return json.dumps({'message':'Both email and password are required'}), 400
    
    user = User.query.filter_by(email=request.json['email']).first()
    if not user:
        return make_response("User not found with the provided email.", 401, {'WWW-Authenticate': 'Basic realm:"Authentication Failed!"'})
    
    if not bcrypt.check_password_hash(user.password, request.json['password']):
        return make_response("Incorrect Password.", 401, {'WWW-Authenticate': 'Basic realm:"Authentication Failed!"'})

    if user and bcrypt.check_password_hash(user.password, request.json['password']):
        token = jwt.encode({'email': request.json['email'],'username':user.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=25)}, Config.SECRET_KEY, algorithm='HS256')
        return json.dumps({'token':token}), 200
    
    
@api.route('/api/unauthorized')
def unauth():
    return json.dumps({'message':'Welcome to Flask Blog'})

@api.route('/api/authorized')
@api.route('/api/authorized/post/delete/<int:post_id>', methods=['DELETE'])
@api.route('/api/authorized/post/update/<int:post_id>', methods=['PUT'])
@api.route('/api/authorized/post/new', methods=['POST'])
@token_required
def auth(post_id=None):
    # Create a new post
    if request.method == 'POST':
        if request.json:
            author = User.query.filter_by(username=g.current_user['username']).first_or_404()

            if request.json['author'] != g.current_user['username']:
                return json.dumps({'message':"Forbidden, Incorrect Username"}), 403
            post_new = Post(title=request.json['title'], 
                            content=request.json['content'], 
                            author=author)
            db.session.add(post_new)
            db.session.commit()
        
            return json.dumps({'message':'Post created','post': current_post(post_new)}, indent=4, sort_keys=False, default=str), 201
        
    # Delete the post
    if request.method == 'DELETE':
        if post_id:
            user_post = Post.query.get_or_404(post_id)
            if user_post.author.username != g.current_user['username']:
                return json.dumps({"message":"Forbidden, You can't do that!"}), 403
            db.session.delete(user_post)
            db.session.commit()
            return json.dumps({"message":"Successfully deleted the post"}), 200
    
    if request.method == 'PUT':
        if post_id:
            return update_post(post_id)

    # View all the posts
    user = User.query.filter_by(email=g.current_user['email']).first_or_404()
    posts = Post.query.filter_by(author=user)
    
    return json.dumps({'Posts':all_posts(posts)}, indent=4, sort_keys=False, default=str), 200
    
