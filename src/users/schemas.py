import uuid
from pydantic import BaseModel, Field
from datetime import datetime


class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    password_hash: str = Field(exclude=True)
    created_at: datetime
    updated_at: datetime


class UserCreateModel(BaseModel):
    username: str = Field(max_length=32)
    email: str = Field(max_length=128)
    first_name: str = Field(max_length=64)
    last_name: str = Field(max_length=64)
    password: str = Field(min_length=8, max_length=32)


class UserLoginModel(BaseModel):
    email: str = Field(max_length=128)
    password: str = Field(min_length=8, max_length=32)
