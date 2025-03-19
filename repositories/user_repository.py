from werkzeug.security import generate_password_hash
from app import db
from models import User


class UserRepository:

    def insert(self, data):
        user = User(email=data['email'],
                    username=data['username'],
                    password=generate_password_hash(data['password'], method="scrypt"),
                    verified=data['verified'],
                    token=data['token']
        )
        db.session.add(user)
        db.session.commit()

        return user

    def find_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def find_by_username(self, username):
        return User.query.filter_by(username=username).first()

    def find_by_token(self, token):
        return User.query.filter_by(token=token, verified=False).first()

    def find_by_forgot_password_token(self, token):
        return User.query.filter_by(forgot_password_token=token).first()

    def update(self, data, model=None):
        if model is None:
            model = User.query.filter_by(id=data['id']).first()

        if model is not None:
            if 'email' in data:
                model.email = data['email']
            if 'username' in data:
                model.username = data['username']
            if 'password' in data:
                model.password = data['password']
            if 'verified' in data:
                model.verified = data['verified']
            if 'token' in data:
                model.token = data['token']
            if 'forgot_password_token' in data:
                model.forgot_password_token = data['forgot_password_token']
            if 'password' in data:
                model.password = generate_password_hash(data['password'], method="scrypt")
            db.session.commit()

        model = User.query.filter_by(id=model.id).first()

        return model