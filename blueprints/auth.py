from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, render_template
from flask_cors import cross_origin
from werkzeug.security import check_password_hash
from app import app, token_required
import jwt
from repositories.user_repository import UserRepository
from util.helper import get_user_image, send_mail, token_generator, get_user

auth = Blueprint('auth', __name__)

user_repository = UserRepository()


@auth.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if 'username' not in data.keys():
        return {'success': False, 'message': 'username missing'}, 400
    if 'email' not in data.keys():
        return {'success': False, 'message': 'email missing'}, 400
    if 'password' not in data.keys():
        return {'success': False, 'message': 'password missing'}, 400

    username = data['username']
    email = data['email']
    password = data['password']

    user = user_repository.find_by_email(email)
    if user:
        return {'success': False, 'message': 'user exists'}, 400
    user = user_repository.find_by_username(username)
    if user:
        return {'success': False, 'message': 'user exists'}, 400

    token = token_generator()
    user_repository.insert({
        'email': email,
        'username': username,
        'password': password,
        'verified': False,
        'token': token
    })
    url = app.config['FRONT_BASE_URL'] + '/user/verify/' + token
    send_mail(email, 'Email Verification', url)

    return {'success': True, 'message': 'User created'}


@auth.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if 'email' not in data.keys():
        return {'success': False, 'message': 'email missing'}, 400
    if 'password' not in data.keys():
        return {'success': False, 'message': 'password missing'}, 400
    email = data['email']
    password = data['password']

    user = user_repository.find_by_email(email)
    if not user or not check_password_hash(user.password, password):
        return {'success': False, 'message': 'wrong credentials'}, 401

    token = jwt.encode({'email': user.email, 'expiration': str(datetime.utcnow() + timedelta(minutes=120))},
                       app.config['SECRET_KEY'], algorithm='HS256'
                       )
    verified = user.verified
    if verified is None:
        verified = False

    response = jsonify(
        {'success': True, 'data': {'token': token, 'username': user.username, 'verified': verified,
                                   'avatar': get_user_image(user)}})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@auth.route('/api/user/verify', methods=['POST'])
def user_verification():
    data = request.get_json()
    token = data['token']

    user = user_repository.find_by_token(token=token)
    if user is None:
        return {'success': False, 'message': 'User Not Found'}

    user_repository.update({'token': '', 'verified': True}, user)

    response = jsonify({'success': True, 'message': 'User verified'})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@auth.route('/api/user/verify/request', methods=['POST'])
@token_required
def verification_request():
    user = get_user()
    token = token_generator()
    user_repository.update({'token':token, 'verified': False}, user)
    url = app.config['FRONT_BASE_URL'] + '/user/verify/' + token
    send_mail(user.email, 'Email Verification', url)
    return {'success': True, 'message': 'Verification Sent'}


@auth.route('/api/user/forgot-password', methods=['POST'])
def forgot_password_request():
    data = request.get_json()
    user = user_repository.find_by_email(data['email'])
    if user is None:
        return {'success': False, 'message': 'User Not Found'}
    token = token_generator()
    user_repository.update({'forgot_password_token': token}, user)
    url = app.config['FRONT_BASE_URL'] + '/recover-password/' + token
    send_mail(user.email, 'Password change request', url)

    return {'success': True, 'message': 'Check your email'}

@auth.route('/api/user/recover-password', methods=['POST'])
def recover_password():
    data = request.get_json()
    user = user_repository.find_by_forgot_password_token(data['token'])
    if user is None:
        return {'success': False, 'message': 'User Not Found'}

    user_repository.update({'password': data['password'], 'forgot_password_token':None}, user)

    return {'success': True, 'message': 'Password Changed'}

@auth.route("/", methods=['GET'])
def index():
    return render_template('index.html',)