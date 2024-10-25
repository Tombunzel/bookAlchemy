import os
import sqlalchemy
from flask import Flask, request, render_template, redirect, url_for, flash
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from data_fetcher import add_book_info, get_author_pic_and_summary
from data_models import db, Author, Book

# Get absolute path to 'data/library.sqlite'
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/library.sqlite')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
db.init_app(app)


@app.route('/', methods=['GET', 'POST'])
def home_page():
    """
    home page route that shows all the books
    handles sorting if post-method
    """
    # books joined with authors on relationship
    joined_books = db.session.execute(
        db.select(Book).options(joinedload(Book.author))
    ).scalars().all()
    books_for_html = add_book_info(joined_books)
    if request.method == 'POST':
        sort_by = request.form['sort_by']
        books_for_html = sorted(books_for_html, key=lambda book: book[sort_by])
    return render_template('home.html', books=books_for_html)


@app.route('/search', methods=['GET'])
def search_books():
    """
    search route handling a query and looking through books and authors
    external thumbnail function fetches
    """
    query = request.args.get('query', '')
    if query:
        books = db.session.execute(
            db.select(Book)
            .options(joinedload(Book.author))
            .where(
                or_(
                    Book.title.ilike(f'%{query}%'),
                    Book.author.has(Author.name.ilike(f'%{query}%'))
                )
            )
        ).scalars().all()
        books_for_html = add_book_info(books)
        return render_template('home.html', books=books_for_html)

    return redirect(url_for('home_page'))


@app.route('/book/<int:book_id>', methods=['GET'])
def show_book(book_id):
    """
    renders the book template for a book with book_id
    """
    book = db.session.execute(db.select(Book).where(Book.id == book_id)).scalars().one()
    if book:
        book_for_html = add_book_info([book])
        return render_template('book.html', book=book_for_html[0])
    flash("Something went wrong, couldn't fetch book", "danger")
    return redirect(url_for('home_page'))


@app.route('/author/<int:author_id>')
def show_author(author_id):
    """
    renders the author.html template with an author with author_id
    fetch author img and summary
    """
    author = db.session.execute(db.select(Author).where(Author.id == author_id)).scalars().one()
    if author:
        img_url, summary = get_author_pic_and_summary(author.name)
        author_for_html = {'name': author.name,
                           'birth_date': author.birth_date,
                           'date_of_death': author.date_of_death,
                           'img': img_url,
                           'summary': summary}
        return render_template('author.html', author=author_for_html)
    flash("Something went wrong, couldn't fetch author", "danger")
    return redirect(url_for('home_page'))


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """
    route to delete a book from the database according to book_id.
    if there are no more books of the deleted book's author, delete author from the database
    """
    book = db.session.execute(db.select(Book).where(Book.id == book_id)).scalars().one()
    if book:
        db.session.delete(book)
        db.session.commit()
        flash(f"Book with id {book_id} successfully deleted", "success")
    else:
        flash(f"Book with id {book_id} not found", "danger")
    if not (db.session.execute(
            db.select(Book)
            .where(Book.author_id == book.author_id))
            .scalars().all()):
        author = (db.session.execute(
            db.select(Author)
            .where(Author.id == book.author_id))
            .scalars().one_or_none())
        db.session.delete(author)
        db.session.commit()
        flash(f"No more books from author {author.name}. "
              f"Author removed from database", "success")

    return redirect(url_for('home_page'))


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """
    route that shows a form to add an author to the database
    """
    if request.method == 'POST':
        name = request.form['name']
        birth_date = request.form['birthdate']
        date_of_death = request.form['date_of_death']

        author = Author(
            name=name,
            birth_date=birth_date,
            date_of_death=date_of_death
        )

        db.session.add(author)
        db.session.commit()
        flash(f"author {name} successfully added to the database", "success")
        return redirect(url_for('home_page'))

    return render_template('add_author.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    """
    route that shows a form to add a book to the database
    """
    authors = db.session.execute(db.select(Author).order_by(Author.name.desc())).scalars().all()
    if request.method == 'POST':
        isbn = request.form['isbn']
        title = request.form['title']
        publication_year = request.form['publication_year']
        form_author = request.form['author']
        try:
            author_id = db.session.execute(
                db.select(Author.id)
                .filter(Author.name == form_author)
            ).scalars().one()
        except sqlalchemy.exc.NoResultFound:
            flash("Couldn't find author in database", "danger")
            return redirect(url_for('home_page'))

        book = Book(
            isbn=isbn,
            title=title,
            publication_year=publication_year,
            author_id=author_id
        )

        db.session.add(book)
        db.session.commit()
        flash(f"Book {title} successfully added to the database", "success")
        return redirect(url_for('home_page'))

    return render_template('add_book.html', authors=authors)


if __name__ == "__main__":
    # # creating all tables, only run once
    # with app.app_context():
    #     db.create_all()

    app.run(host="0.0.0.0", port=5000, debug=True)
