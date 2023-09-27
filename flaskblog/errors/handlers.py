# making this file a blueprints just like in users and posts folders
from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)

# for 404 error. Not found
@errors.app_errorhandler(404)
def error_404(error):
    return render_template('errors/404.html'), 404

# forbidden url 
@errors.app_errorhandler(403)
def error_403(error):
    return render_template('errors/403.html'), 403

# for Internal server error
@errors.app_errorhandler(500)
def error_500(error):
    return render_template('errors/500.html'), 500