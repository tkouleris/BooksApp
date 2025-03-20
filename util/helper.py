import os
import pathlib
import random
import string

import jwt
import requests
from flask import request

import models
from app import app


def get_user():
    token = request.headers.get('Authorization').replace('Bearer ', '')
    payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
    email = payload['email']
    return models.User.query.filter_by(email=email).first()


def get_book_image(book):
    image = None
    image_folder = os.path.join(app.config['BOOK_IMAGES_FOLDER'],str(book.user_id))
    image_full_path = os.path.join(image_folder, str(book.id) + '.jpg')
    if pathlib.Path(image_full_path).is_file():
        image = app.config['APP_BASE_URL'] + '/static/book_image/' + str(book.user_id) + '/' + str(
            book.id) + '.jpg'
    return image


def get_user_image(user):
    image = app.config['APP_BASE_URL'] + '/static/default_image/avatar.png'
    image_folder = app.config['USER_IMG_FOLDER']
    image_full_path = os.path.join(image_folder, str(user.id) + '.jpg')
    if pathlib.Path(image_full_path).is_file():
        image = app.config['APP_BASE_URL'] + '/static/user_image/' + str(user.id) + '.jpg'
    return image

def order_change(records, id, new_position):
    item_to_move = next((item for item in records if item.id == id), None)
    if not item_to_move:
        return records  # If item not found, return the original list

    # Remove the item from the list
    records = [item for item in records if item.id != id]

    # Insert the item at the new position
    records.insert(new_position - 1, item_to_move)

    # Recalculate the order field
    for index, item in enumerate(records, start=1):
        item.order = index

    return records
def send_mail(to, subject, body):

    domain = app.config['MAILGUN_DOMAIN']
    apiKey = app.config['MAILGUN_API_KEY']
    from_mail = app.config['MAILGUN_FROM']

    response = requests.post(
        f"https://api.eu.mailgun.net/v3/{domain}/messages",
        auth=("api", apiKey),
        data={
            "from": from_mail,
            "to": to,
            "subject": subject,
            "text": body
        }
    )
    return response

def token_generator(size=30, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))