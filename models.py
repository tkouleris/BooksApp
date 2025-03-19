from app import db
from util.helper import get_book_image, get_user_image


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(1000), nullable=False, unique=True)
    password = db.Column(db.Text(), nullable=False)
    verified = db.Column(db.Boolean, unique=False, default=True)
    token = db.Column(db.Text(), nullable=True)
    forgot_password_token = db.Column(db.Text(), nullable=True)

    def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'avatar': get_user_image(self),
            'verified': self.verified
        }


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(1000), nullable=False)
    description = db.Column(db.String(1000), nullable=False)

    def serialize(self):
        record = ToRead.query.filter_by(user_id=self.user_id, book_id=self.id).first()
        is_in_toread_list = False if record is None else True
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'image': get_book_image(self),
            'toread':is_in_toread_list
        }


class Readings(db.Model):
    __tablename__ = 'readings'
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    started = db.Column(db.DateTime, nullable=True)
    ended = db.Column(db.DateTime, nullable=True)

    def serialize(self):
        book = Book.query.filter_by(id=self.book_id).first()
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book': book.serialize(),
            'started': self.started.strftime("%Y-%m-%d") if self.started is not None else ' - ',
            'ended': self.ended.strftime("%Y-%m-%d") if self.ended is not None else ' - '
        }


class ToRead(db.Model):
    __tablename__ = 'to_read'
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    order = db.Column(db.Integer, nullable=False)

    def serialize(self):
        book = Book.query.filter_by(id=self.book_id).first()
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book': book.serialize(),
        }