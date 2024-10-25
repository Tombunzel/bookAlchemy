from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    """
    class of author table with relationship to book table
    """
    __tablename__ = 'authors'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    birth_date: Mapped[str] = mapped_column(nullable=True)
    date_of_death: Mapped[str] = mapped_column(nullable=True)

    # Relationship to Book
    books = relationship("Book", back_populates="author")

    def __repr__(self):
        """
        string representation
        """
        return (f'{self.id}: {self.name} '
                f'({self.birth_date.split('-')[0]} - '
                f'{self.date_of_death.split('-')[0]})')


class Book(db.Model):
    """
    class of book table with relationship to author table
    """
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    isbn: Mapped[int] = mapped_column(unique=True)
    title: Mapped[str] = mapped_column(nullable=False)
    publication_year: Mapped[int] = mapped_column(nullable=True)
    author_id: Mapped[int] = mapped_column(ForeignKey('authors.id'), nullable=False)

    # Relationship to Author
    author = relationship("Author", back_populates="books")

    def __repr__(self):
        """
        string representation
        """
        return f'{self.id}: {self.title} ({self.publication_year})'
