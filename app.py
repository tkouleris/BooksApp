import datetime
import functools
from flask import Flask, request
import os
from dotenv import load_dotenv, find_dotenv
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import jwt
from flask_cors import CORS


def token_required(func):
    @functools.wraps(func)
    def decorated(*args, **kwargs):
        if 'Authorization' not in request.headers.keys():
            return {'success': False, 'message': 'Missing token'}, 400
        try:
            token = request.headers.get('Authorization').replace('Bearer ', '')
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')

            expires = payload['expiration'][:16]
            expires_timestamp = datetime.datetime.strptime(expires, "%Y-%m-%d %H:%M").timestamp()
            now_timestamp = datetime.datetime.utcnow().timestamp()
            if now_timestamp > expires_timestamp:
                return {'success': False, 'message': 'Token expired'}, 400

            email = payload['email']
            user = models.User.query.filter_by(email=email).first()
            if not user:
                return {'success': False, 'message': 'Invalid username'}, 400
            return func(*args, **kwargs)
        except Exception as e:
            print(repr(e))
            return {'success': False, 'message': "There was an error"}, 400

    return decorated


def init_blueprints():
    from blueprints import display as display_blueprint
    app.register_blueprint(display_blueprint.display)

    from blueprints import auth as auth_blueprint
    app.register_blueprint(auth_blueprint.auth)

    from blueprints import library as library_blueprint
    app.register_blueprint(library_blueprint.library)

    from blueprints import readings as readings_blueprint
    app.register_blueprint(readings_blueprint.readings)

    from blueprints import profile as profile_blueprint
    app.register_blueprint(profile_blueprint.profile)

    from blueprints import to_read as to_read_blueprint
    app.register_blueprint(to_read_blueprint.to_read)

    from blueprints import dashboard as dashboard_blueprint
    app.register_blueprint(dashboard_blueprint.dashboard)


def create_app():
    load_dotenv(find_dotenv(usecwd=True))
    app = Flask(__name__)
    app.config['APP_BASE_URL'] = os.getenv('APP_BASE_URL')
    app.config['FRONT_BASE_URL'] = os.getenv('FRONT_BASE_URL')
    app.config['BOOK_IMAGES_FOLDER'] = os.getenv('BOOK_IMAGES_FOLDER')
    app.config['USER_IMG_FOLDER'] = os.getenv('USER_IMAGES_FOLDER')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')

    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
    app.config['MAILGUN_API_KEY'] = os.getenv('MAILGUN_API_KEY')
    app.config['MAILGUN_DOMAIN'] = os.getenv('MAILGUN_DOMAIN')
    app.config['MAILGUN_FROM'] = os.getenv('MAILGUN_FROM')

    return app


app = create_app()
CORS(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
import models

mail = Mail(app)

init_blueprints()

if __name__ == '__main__':
    app.run()
