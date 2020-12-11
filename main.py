from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy


# Application definition
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///storage.db'


# Error handler
@app.errorhandler(404)
def page_not_found(e):
    return {'error': 'page is not found'}


# Database definition
db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    preview = db.Column(db.Text, nullable=True)

db.create_all()


# Response data
def response_success(data={}):
    default = {'status': 'ok'}
    return {**default, **data}

def response_failed(data={}):
    default = {'status': 'failed'}
    return {**default, **data}

def serialize_book_detail(book):
    return {
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'preview': book.preview,
    }


# List of available books
@app.route('/books', methods=['GET'])
def book_list():
    books = Book.query.all()
    books = [serialize_book_detail(book) for book in books]
    return response_success({'result': books})


# Add book to inventory
@app.route('/books', methods=['POST'])
def book_add():
    req_data = request.get_json()
    book_title = req_data.get('title')
    book_author = req_data.get('author')
    book_preview = req_data.get('preview')

    book = Book(
        title=book_title, 
        author=book_author, 
        preview=book_preview)

    try:
        db.session.add(book)
        db.session.commit()
        return response_success()
    except Exception as e:
        return response_failed()


# Get existing book in inventory
@app.route('/books/<book_id>', methods=['GET'])
def book_detail(book_id):
    book = Book.query.filter_by(id=book_id)
    book = book.first()

    if book == None:
        return response_failed({
            'message': f'Book #{book_id} does not exist'
        })

    book = serialize_book_detail(book)
    return response_success({'result': book})


# Edit existing book in inventory
@app.route('/books/<book_id>', methods=['PUT'])
def book_update(book_id):
    book = Book.query.filter_by(id=book_id)
    book = book.first()

    if book == None:
        return response_failed({
            'message': f'Book #{book_id} does not exist'
        })

    req_data = request.get_json()

    try:
        book.title = req_data.get('title')
        book.author = req_data.get('author')
        book.preview = req_data.get('preview')
        db.session.commit()
        return response_success()
    except Exception as e:
        return response_failed()


# Delete exiting book in inventory
@app.route('/books/<book_id>', methods=['DELETE'])
def book_delete(book_id):
    book = Book.query.filter_by(id=book_id)
    book = book.first()

    if book == None:
        return response_failed({
            'message': f'Book #{book_id} does not exist'
        })

    try:
        db.session.delete(book)
        db.session.commit()
        return response_success()
    except Exception as e:
        return response_failed()


# Running the application
if __name__ == '__main__':
    app.run(debug=True)