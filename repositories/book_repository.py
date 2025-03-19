from sqlalchemy import and_

from app import db
from models import Book


class BookRepository:

    def insert(self, data):
        new_book = Book(title=data['title'], description=data['description'], user_id=data['user_id'])
        db.session.add(new_book)
        db.session.commit()

        return new_book

    def find_by_id(self, id):
        return Book.query.filter_by(id=id).first()

    def find_by_id_and_user_id(self, id, user_id):
        return Book.query.filter_by(id=id, user_id=user_id).first()

    def find_by_title(self, title):
        return Book.query.filter_by(title=title).first()

    def find_user_books(self, user_id, per_page=None, page=None, title=None):
        if title is not None:
            query = Book.query.filter_by(user_id=user_id).filter(Book.title.like("%{}%".format(title)))
        else:
            query = Book.query.filter_by(user_id=user_id)

        if per_page is not None and page is not None:
            offset = (page - 1) * per_page
            query = query.limit(per_page).offset(offset)
        return query.all()

    def update(self, data, model=None):
        if model is None:
            model = Book.query.filter_by(id=data['id']).first()

        if model is not None:
            if 'title' in data:
                model.title = data['title']
            if 'description' in data:
                model.description = data['description']
            db.session.commit()
        return model

    def delete(self, bookId):
        book_to_delete = Book.query.filter_by(id=bookId).first()
        db.session.delete(book_to_delete)
        db.session.commit()

