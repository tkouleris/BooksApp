from app import db
from models import Readings
from sqlalchemy import text


class ReadingsRepository:

    def insert(self, data):
        started = None
        if 'started' in data:
            started = data['started']
        ended = None
        if 'ended' in data:
            ended = data['ended']
        reading = Readings(book_id=data['book_id'], user_id=data['user_id'], started=started,
                           ended=ended)
        db.session.add(reading)
        db.session.commit()

        return reading

    def find_by_id(self, id):
        return Readings.query.filter_by(id=id).first()

    def update(self, data, model=None):
        if model is None:
            model = Readings.query.filter_by(id=data['id']).first()

        if model is not None:
            if 'started' in data:
                model.started = data['started']
            if 'ended' in data:
                model.ended = data['ended']
            if 'book_id' in data:
                model.book_id = data['book_id']
            db.session.commit()
        return model

    def find_current_readings(self, user_id):
        return Readings.query.filter_by(ended=None, user_id=user_id).all()

    def find_latest_finished(self, user_id, num_of_records=3):
        return (Readings.query.filter(Readings.ended != None, Readings.user_id == user_id)
                .order_by(Readings.ended.desc())
                .limit(num_of_records).all())

    def find_all_readings(self, user_id, per_page=None, page=None):
        query = Readings.query.filter_by(user_id=user_id).order_by(Readings.started.desc())
        if per_page is not None and page is not None:
            offset = (page - 1) * per_page
            query = query.limit(per_page).offset(offset)
        return query.all()

    def find_user_reading(self, id, user_id):
        return Readings.query.filter_by(id=id, user_id=user_id).first()

    def find_reading_by_book(self, book_id):
        return Readings.query.filter_by(book_id=book_id).order_by(Readings.started.desc()).all()

    def find_books_read(self, user_id):
        query = "SELECT DISTINCT book_id FROM readings WHERE user_id = " + str(
            user_id) + " AND started IS NOT NULL AND ended IS NOT NULL"
        sql = text(query)
        result = db.session.execute(sql)
        output = []
        for row in result:
            output.append(row.book_id)
        return output

    def find_books_per_year(self, user_id):
        query = "SELECT COUNT(book_id) as books_per_year, YEAR(ended) as year FROM readings WHERE user_id = " + str(
            user_id) + " AND started IS NOT NULL AND ended IS NOT NULL GROUP BY YEAR(ended) ORDER BY YEAR(ended)"
        sql = text(query)
        result = db.session.execute(sql)
        return result

    def delete(self, readId, userId):
        record_to_delete = Readings.query.filter_by(id=readId, user_id=userId).first()
        db.session.delete(record_to_delete)
        db.session.commit()
