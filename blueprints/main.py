from flask import Blueprint, render_template, send_from_directory

main = Blueprint('main', __name__)


# @main.route("/", methods=['GET'])
# def index():
#     return render_template('index.html', )


@main.route('/', defaults={'path': ''})
@main.route('/<path:path>')
def serve_react_app(path):
    if path != "" and not path.startswith("static") and not path.startswith("api"):
        return render_template('index.html')
    else:
        return send_from_directory('static', path)