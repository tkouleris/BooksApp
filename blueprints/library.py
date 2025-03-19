import math
import os
from flask import Blueprint, jsonify, request
from app import token_required, app
from repositories.readings_repository import ReadingsRepository
from util.helper import get_user
from repositories.book_repository import BookRepository

library = Blueprint('library', __name__)

book_repository = BookRepository()
readings_repository = ReadingsRepository()

@library.route("/api/library/book/", methods=['POST'])
@token_required
def store_book():
    # Get the JSON data (optional)
    book_data = request.form.to_dict()  # Converts the form data to a dictionary
    user = get_user()
    book_data['user_id'] = user.id
    if 'book_id' in book_data:
        book_data['id'] = book_data['book_id']
        book = book_repository.update(book_data)
    else:
        book = book_repository.insert(book_data)
        book_data['id'] = book.id

    book_id = book.id
    upload_folder = app.config['BOOK_IMAGES_FOLDER'] + '/' +str(user.id)
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    file = None
    if 'file' in request.files:
        file = request.files['file']
    if file:
        file_path = os.path.join(upload_folder, str(book_id) + '.jpg')
        file.save(file_path)

    return jsonify({
        'success': True,
        'data': book_data
    }), 200


@library.route("/api/library/book/<book_id>", methods=['GET'])
@token_required
def get_book(book_id):
    user = get_user()
    book = book_repository.find_by_id_and_user_id(book_id, user.id)
    if book is None:
        return jsonify({
            'success': False,
            'message': "Not Found"
        }), 404
    book = book.serialize()

    readings = readings_repository.find_reading_by_book(book_id)
    book_readings = []
    for book_reading in readings:
        book_readings.append(book_reading.serialize())

    return jsonify({
        'success': True,
        'data': { 'book': book, 'readings': book_readings }
    }), 200


@library.route("/api/library/books/", methods=['GET'])
@token_required
def get_books():
    user = get_user()
    current_page = request.args.get('page')
    search_title = request.args.get('title')
    total_pages = 0
    if current_page is not None:
        current_page = int(current_page)
        per_page = 12
        total_items = book_repository.find_user_books(user.id, None, None, search_title)
        total_items = len(total_items)
        total_pages = math.ceil(total_items / per_page)
        books = book_repository.find_user_books(user.id, per_page, current_page, search_title)
    else:
        current_page = 0
        books = book_repository.find_user_books(user.id)

    json_books = []
    for book in books:
        json_books.append(book.serialize())

    output = {
        'success': True,
        'data': {
            'books':json_books,
        },
    }

    if total_pages > 0 and current_page > 0:
        output['data']['total_pages'] = total_pages
        output['data']['current_page'] = current_page

    return jsonify(output), 200


@library.route("/api/library/book/<book_id>", methods=['DELETE'])
@token_required
def delete_book(book_id):
    book_repository.delete(book_id)
    return jsonify({
        'success': True,
    }), 201
