from app import db
from models import ToRead

class ToReadRepository:

    def store(self, data):
        new_record = ToRead(book_id=data['book_id'], user_id=data['user_id'], order=data['order'])
        db.session.add(new_record)
        db.session.commit()

    def find_by_book(self,user_id, book_id):
        return ToRead.query.filter_by(user_id=user_id, book_id=book_id).first()

    def find_by_user(self, user_id):
        return ToRead.query.filter_by(user_id=user_id).order_by(ToRead.order).all()

    def find_by_id(self, id, user_id):
        return ToRead.query.filter_by(id=id, user_id=user_id).first()

    def update(self, data, model=None):
        if model is None:
            model = ToRead.query.filter_by(id=data['id']).first()

        if model is not None:
            if 'order' in data:
                model.order = data['order']
            db.session.commit()
        return model

    def delete_record(self, id=None, to_read_record=None):
        if id is None and to_read_record is None:
            return False
        if id is not None:
            to_read_record = ToRead.query.filter_by(id=id).first()

        db.session.delete(to_read_record)
        db.session.commit()
        return True
