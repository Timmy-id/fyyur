from flask import Blueprint, render_template


errors = Blueprint('errors', __name__)


@errors.app_errorhandler(400)
def bad_request_error(error):
    return render_template('errors/400.html'), 400


@errors.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@errors.app_errorhandler(405)
def invalid_method_error(error):
    return render_template('errors/405.html'), 304


@errors.app_errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500
