import os
import zipfile
from typing import List

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

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


@app.post("/books/", response_model=List[schemas.Book])
def create_book(books: List[schemas.BookCreate], db: Session = Depends(get_db)):
    created_books = []
    for book in books:
        # 创建书籍
        created_book = crud.create_book(db=db, book=book)
        created_books.append(created_book)
    return created_books


@app.post("/users/", response_model=List[schemas.User])
def create_user(users: List[schemas.UserCreate], db: Session = Depends(get_db)):
    created_users = []
    for user in users:
        # 检查邮箱是否注册过
        db_user = crud.get_user_by_email(db, email=user.email)
        if db_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        # 创建用户
        created_user = crud.create_user(db=db, user=user)
        created_users.append(created_user)  # 将用户对象转换为字典并添加到列表中
    return created_users


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


@app.post("/send_images")
async def send_images(files: List[UploadFile] = File(...), label: str = Form(None)):
    count = 0
    for file in files:
        with open(f'{count}.jpg', 'wb') as f:
            f.write(await file.read())
        count += 1
    return {"res": len(files)}


@app.get("/get_image/{image_index}")
async def get_image(image_index: int):
    try:
        # 根据图片索引构建文件路径
        file_path = f"{image_index}.jpg"
        # 返回文件
        return FileResponse(file_path, media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=404, detail="Image not found")


@app.get("/get_all_images")
async def get_all_images():
    try:
        # 获取所有上传的图片文件的列表
        image_files = [filename for filename in os.listdir() if filename.endswith('.jpg')]
        if not image_files:
            raise HTTPException(status_code=404, detail="No images found")

        # 创建一个 zip 文件，用于存储所有图片
        with zipfile.ZipFile("images.zip", "w") as zipf:
            # 将所有图片文件添加到 zip 文件中
            for filename in image_files:
                zipf.write(filename)

        # 返回 zip 文件给客户端
        return FileResponse("images.zip", media_type="application/zip", filename="images.zip")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create zip file")


if __name__ == '__main__':
    uvicorn.run('main:app')
