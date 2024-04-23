import random
import string

from sqlalchemy.orm import Session
from library_sys import models, schemas


def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_name(db: Session, name: str):
    name_lower = name.lower()
    return db.query(models.User).filter(models.User.name.lower() == name_lower).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_book(db: Session, book_code: str):
    return db.query(models.Book).filter(models.Book.code == book_code).first()


def get_book_by_title(db: Session, book_title: str):
    return db.query(models.Book).filter(models.Book.title == book_title).first()


def get_book_by_author(db: Session, author: str):
    author_lower = author.lower()
    return db.query(models.Book).filter(models.Book.author.lower() == author_lower).first()


def check_book_borrowed_by_user(db: Session, user_id: str, book_code: str) -> bool:
    book = db.query(models.Book).filter_by(code=book_code).first()
    if book and book.user_id == user_id:
        return True
    return False


def get_books(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Book).offset(skip).limit(limit).all()


def get_borrow_record(db: Session, user_id: str, book_code: str):
    return db.query(models.Borrow).filter(models.Borrow.user_id == user_id,
                                          models.Borrow.book_code == book_code).first()


def generate_user_id() -> str:
    return str(random.randint(100000, 999999))


def generate_book_code() -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


def create_user(db: Session, user: schemas.UserCreate):
    user_id = generate_user_id()
    db_user = models.User(email=user.email, name=user.name, id=user_id)
    db.add(db_user)  # 添加到会话
    db.commit()  # 提交到数据库
    db.refresh(db_user)  # 刷新数据库
    return db_user


def create_book(db: Session, book: schemas.BookCreate):
    book_code = generate_book_code()
    db_book = models.Book(title=book.title, author=book.author, isbn_number=book.isbn_number,
                          available=True, code=book_code)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

