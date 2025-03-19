from flask import Blueprint, jsonify, request
from app import token_required
from repositories.toread_repository import ToReadRepository
from util.helper import get_user, order_change

to_read = Blueprint('to_read', __name__)

toread_repository = ToReadRepository()

@to_read.route("/api/to_read/store/", methods=['POST'])
@token_required
def store_to_read():
    user = get_user()
    data = request.get_json()
    data['user_id'] = user.id
    records = toread_repository.find_by_user(user.id)
    data['order'] = len(records) + 1

    record = toread_repository.find_by_book(data['user_id'], data['book_id'])
    if record is not None:
        return jsonify({
            'success': False,
            'message': "Book already in the list"
        }), 200

    toread_repository.store(data)

    return jsonify({
        'success': True,
    }), 200

@to_read.route("/api/to_read/reorder/", methods=['POST'])
@token_required
def swap_order():
    user = get_user()
    data = request.get_json()

    records = toread_repository.find_by_user(user.id)
    record_2 = toread_repository.find_by_id(data['id_2'], user.id)

    records = order_change(records, data['id_1'], record_2.order)
    for record in records:
        toread_repository.update({"order":record.order}, record)

    book_list = toread_repository.find_by_user(user.id)

    to_read = []
    for book in book_list:
        to_read.append(book.serialize())

    return jsonify({
        'success': True,
        'data': to_read
    }), 200


@to_read.route("/api/to_read/list/", methods=['GET'])
@token_required
def to_read_list():
    user = get_user()
    book_list = toread_repository.find_by_user(user.id)

    to_read = []
    for book in book_list:
        to_read.append(book.serialize())

    return jsonify({
        'success': True,
        'data':to_read
    }), 200

@to_read.route("/api/to_read/book/<book_id>", methods=['DELETE'])
@token_required
def remove_from_read_list(book_id):

    user = get_user()
    book_to_read_record = toread_repository.find_by_book(user.id, book_id)
    toread_repository.delete_record(None, book_to_read_record)

    book_list = toread_repository.find_by_user(user.id)

    to_read = []
    for book in book_list:
        to_read.append(book.serialize())

    return jsonify({
        'success': True,
        'data':to_read
    }), 200