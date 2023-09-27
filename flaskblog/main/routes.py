from flask import render_template,request,Blueprint
from flaskblog.models import Post

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home')                                                                                             # same route leads to the same home page
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=7)                                  # paginate is sqlalchemy's method
    return render_template('home.html',posts=posts)                                                             # the argument posts is equal to posts list above and using it in html

@main.route('/about')
def about():
    return render_template('about.html',title='About')