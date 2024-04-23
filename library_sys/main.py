import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from library_sys import crud, models, schemas
from library_sys.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# 依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/books/", response_model=schemas.Book)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    # 创建书籍
    return crud.create_book(db, book)


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 检查邮箱是否注册过
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # 返回所有用户
    db_users = crud.get_users(db, skip=skip, limit=limit)
    return db_users


@app.get("/books/", response_model=list[schemas.Book])
def read_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # 返回所有书籍
    db_books = crud.get_books(db, skip=skip, limit=limit)
    return db_books


@app.put("/books/borrow/")
def borrow_book(user_id: str, book_code: str, db: Session = Depends(get_db)):
    """Borrow a book."""
    # 检查用户是否存在
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # 检查书籍是否存在且可借
    book = crud.get_book(db, book_code)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    if not book.available:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book not available for borrowing")

    # 更新书籍的状态为不可借，并关联到用户
    book.available = False
    book.user_id = user.id
    db.commit()

    # 创建借书记录
    borrow = models.Borrow(user_id=user.id, book_code=book.code)
    db.add(borrow)
    db.commit()

    # 返回借书记录
    return {"user_id": user_id, "book_code": book_code}


# 还书
@app.put("/books/return/")
def return_book(user_id: str, book_code: str, db: Session = Depends(get_db)):
    """Return a borrowed book."""
    # 检查用户是否存在
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # 检查书籍是否被该用户借出
    book_available = crud.check_book_borrowed_by_user(db, user_id, book_code)
    if not book_available:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This book is not borrowed by the user")

    # 更新书籍的状态为可借，并解除与用户的关联
    book = crud.get_book(db, book_code)
    book.available = True
    book.user_id = None
    db.commit()

    # 删除借书记录
    borrow_record = crud.get_borrow_record(db, user_id, book_code)
    db.delete(borrow_record)
    db.commit()

    return {"message": "Book returned successfully"}


if __name__ == '__main__':
    uvicorn.run('main:app')

