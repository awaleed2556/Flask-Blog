from flask import Blueprint, Response, request, make_response
from flaskblog.models import User, Post
from flaskblog import db,bcrypt
from flaskblog.config import Config
from flaskblog.users.utils import gravatarImage
import json, jwt, datetime

api = Blueprint('api', __name__)


@api.route('/api/userdata')
@api.route('/api/userdata/<int:id>')
def UserID(id=None):
    if id:
        users = User.query.get_or_404(id)
        return Response(
            response=json.dumps({'id':users.id, 'username':users.username, 'email':users.email}),
            status=200,
            mimetype='application/json')
    
    users = User.query.all()
    output = []
    for user in users:
        user_data = {'id':user.id, 'username':user.username, 'email':user.email}
        output.append(user_data)
    return Response(
        response=json.dumps({"Users":output}),
        status=200,
        mimetype='application/json'
    )

@api.route('/api/postdata')
@api.route('/api/postdata/<int:id>')
def PostID(id=None):
    if id:
        post = Post.query.get_or_404(id)
        return Response(
            response=json.dumps({"id":post.id,"title":post.title,"date posted":post.date_posted,"content":post.content,"author":post.author.username}, indent=4, sort_keys=True, default=str),
            status=200,
            mimetype='application/json'
        )
    
    posts = Post.query.all()
    output = []
    for post in posts:
        post_data = {"id":post.id,"title":post.title,"date posted":post.date_posted,"content":post.content,"author":post.author.username}
        output.append(post_data)
    return Response(
        response=json.dumps({"Posts":output}, indent=4, sort_keys=True, default=str),
        status=200,
        mimetype='application/json'
    )

@api.route('/api/register', methods=['POST'])
def registerUser():
    hashed_password = bcrypt.generate_password_hash(request.json['password']).decode('utf-8')
    pfpLink = gravatarImage(request.json['email'])
    user = User(username=request.json['username'], email=request.json['email'], password=hashed_password, gravatar_url=pfpLink)
    db.session.add(user)
    db.session.commit()
    return Response(
        response=json.dumps({'message':'Fuck You'}),
        status=201,
        mimetype='application/json'
    )

@api.route('/api/login', methods=['POST'])
def loginUser():
    user = User.query.filter_by(email=request.json['email']).first()
    
    if user and bcrypt.check_password_hash(user.password, request.json['password']):
        token = jwt.encode({'email': request.json['email'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5)}, Config.SECRET_KEY)
        return json.dumps({'token':token}), 200
    
    else:
        return make_response('Unable to verify',403, {'WWW-Authenticate':'Basic realm:"Authenticate Failed!"'})