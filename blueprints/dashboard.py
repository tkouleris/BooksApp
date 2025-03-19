from flask import Blueprint, jsonify

from app import token_required, db
from repositories.book_repository import BookRepository
from repositories.readings_repository import ReadingsRepository
from repositories.toread_repository import ToReadRepository
from util.helper import get_user

dashboard = Blueprint('dashboard', __name__)

book_repository = BookRepository()
readings_repository = ReadingsRepository()
toread_repository = ToReadRepository()

@dashboard.route("/api/dashboard/", methods=['GET'])
@token_required
def index():
    user = get_user()

    books = book_repository.find_user_books(user.id)
    total_books = len(books)

    currently_reading = readings_repository.find_current_readings(user.id)
    total_currently_reading = len(currently_reading)
    to_read_books = toread_repository.find_by_user(user.id)
    total_to_read_books = len(to_read_books)

    books_read = readings_repository.find_books_read(user.id)
    total_read_books = 0
    for row in books_read:
        total_read_books += 1

    books_per_year = readings_repository.find_books_per_year(user.id)
    labels = []
    data = []
    for record in books_per_year:
        labels.append(record[1])
        data.append(record[0])

    return jsonify({
        'success': True,
        'data': {
            'total_books':total_books,
            'total_currently_reading':total_currently_reading,
            'total_to_read_books':total_to_read_books,
            'read_percentage': (total_read_books / total_books) * 100,
            'char_data': {
                'labels': labels,
                'data': data
            }
        }
    }), 200