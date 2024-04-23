from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.orm import relationship
from sql_app.database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(String(255), primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    name = Column(String(255))
    books = relationship("Book", back_populates="borrower")


class Book(Base):
    __tablename__ = 'books'
    code = Column(String(255), primary_key=True, index=True)
    title = Column(String(255))
    author = Column(String(255))
    isbn_number = Column(String(255), unique=True, index=True)
    available = Column(Boolean, default=True)
    user_id = Column(String(255), ForeignKey('users.id', ondelete="CASCADE"))
    borrower = relationship("User", back_populates="books")


class Borrow(Base):
    __tablename__ = 'borrow'
    user_id = Column(String(255), ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
    book_code = Column(String(255), ForeignKey('books.code', ondelete="CASCADE"), primary_key=True)