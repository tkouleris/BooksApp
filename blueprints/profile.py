import os

from flask import Blueprint, jsonify, request

from app import token_required, app
from repositories.user_repository import UserRepository
from util.helper import get_user
from werkzeug.security import generate_password_hash

profile = Blueprint('profile', __name__)

user_repository = UserRepository()

@profile.route("/api/profile", methods=['GET'])
@token_required
def get_profile():
    user = get_user()
    return jsonify({
        'success': True,
        'data': user.serialize()
    }), 200



@profile.route("/api/profile", methods=['POST'])
@token_required
def store_profile():
    user = get_user()
    data = request.form.to_dict()
    if 'email' in data:
        data['verified'] = 0

    user = user_repository.update(data, user)

    upload_folder = app.config['USER_IMG_FOLDER']

    file = None
    if 'file' in request.files:
        file = request.files['file']
    if file:
        file_path = os.path.join(upload_folder, str(user.id) + '.jpg')
        file.save(file_path)

    return jsonify({
        'success': True,
        'data': user.serialize()
    }), 200