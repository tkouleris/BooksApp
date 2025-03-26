from flask import Blueprint, render_template, send_from_directory

main = Blueprint('main', __name__)


@main.route('/', defaults={'path': ''})
@main.route('/<path:path>')
def serve_react_app(path):
    return render_template('index.html')