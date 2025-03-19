import math

from flask import Blueprint, jsonify, request
from app import token_required

from repositories.readings_repository import ReadingsRepository
from repositories.user_repository import UserRepository
from util.helper import get_user


readings = Blueprint('readings', __name__)

readings_repository = ReadingsRepository()
user_repository = UserRepository()


@readings.route("/api/readings/store/", methods=['POST'])
@token_required
def store_reading():
    user = get_user()
    data = request.get_json()
    data['user_id'] = user.id
    if 'reading_id' in data.keys():
        reading = readings_repository.find_by_id(data['reading_id'])
        reading = readings_repository.update(data, reading)
    else:
        reading = readings_repository.insert(data)

    return jsonify({
        'success': True,
        'data': reading.serialize()
    }), 200


@readings.route("/api/readings/latest/<username>", methods=['GET'])
def get_latest_readings(username):
    user = user_repository.find_by_username(username)
    current_readings_db = readings_repository.find_current_readings(user.id)

    current_readings = []
    for current_reading in current_readings_db:
        current_readings.append(current_reading.serialize())

    latest_readings_db = readings_repository.find_latest_finished(user.id)

    latest_readings = []
    for latest_reading in latest_readings_db:
        latest_readings.append(latest_reading.serialize())

    return jsonify({
        'success': True,
        'data': {
            'current_readings': current_readings,
            'latest_readings': latest_readings
        }
    }), 200


@readings.route("/api/readings/all/", methods=['GET'])
@token_required
def get_all_readings():
    user = get_user()
    current_page = request.args.get('page')

    total_pages = 0
    if current_page is not None:
        current_page = int(current_page)
        per_page = 12
        total_items = readings_repository.find_all_readings(user.id)
        total_items = len(total_items)
        total_pages = math.ceil(total_items / per_page)
        all_readings_db = readings_repository.find_all_readings(user.id, per_page, current_page)
    else:
        all_readings_db = readings_repository.find_all_readings(user.id)

    all_readings = []
    for all_reading_db in all_readings_db:
        all_readings.append(all_reading_db.serialize())
    output = {
        'success': True,
        'data': {
            'readings': all_readings,
        },
    }

    if total_pages > 0 and current_page > 0:
        output['data']['total_pages'] = total_pages
        output['data']['current_page'] = current_page

    return jsonify(output), 200


@readings.route("/api/readings/reading/<id>", methods=['GET'])
@token_required
def get_reading(id):
    user = get_user()
    reading = readings_repository.find_user_reading(id, user.id)
    if reading is None:
        return jsonify({
            'success': False,
            'message': "Not Found"
        }), 404

    return jsonify({
        'success': True,
        'data': reading.serialize()
    }), 200


@readings.route("/api/readings/reading/<id>", methods=['DELETE'])
@token_required
def delete_reading(id):
    user = get_user()
    readings_repository.delete(id, user.id)

    return jsonify({
        'success': True,
    }), 201
