from flask import Blueprint, jsonify

from repositories.readings_repository import ReadingsRepository
from repositories.user_repository import UserRepository

display = Blueprint('display', __name__)

user_repository = UserRepository()
readings_repository = ReadingsRepository()


@display.route("/api/display/<username>", methods=['GET'])
def show(username):
    user = user_repository.find_by_username(username)
    if user is None:
        return jsonify({
            'success': False,
            'message': 'User not found'
        }), 404

    current_readings_db = readings_repository.find_current_readings(user.id)
    current_readings = []
    for current_reading in current_readings_db:
        current_readings.append(current_reading.serialize())

    latest_readings_db = readings_repository.find_latest_finished(user.id, 3)
    latest_readings = []
    for latest_reading in latest_readings_db:
        latest_readings.append(latest_reading.serialize())

    return jsonify({
        'success': True,
        'data':{
            'user': user.serialize(),
            'current_readings':current_readings,
            'latest_readings': latest_readings
        }
    }), 200
