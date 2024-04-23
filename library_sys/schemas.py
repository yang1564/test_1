from typing import List, Optional
from pydantic import BaseModel, field_validator


class BookBase(BaseModel):
    title: str
    author: str
    isbn_number: str
    code: Optional[str]


class BookCreate(BookBase):
    available: bool = True


class Book(BookCreate):
    user_id: Optional[str]

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    name: str
    email: str


class UserCreate(UserBase):
    id: Optional[str]

    @field_validator('name')
    def name_must_not_contain_digits(cls, v):
        if any(char.isdigit() for char in v):
            raise ValueError('name must not contain digits')
        return v.title()


class User(UserCreate):
    books: List[Book]

    class Config:
        from_attributes = True
