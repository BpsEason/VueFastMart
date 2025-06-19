from pydantic import BaseModel, EmailStr, validator

class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("密碼需至少 8 個字符")
        return v

class User(BaseModel):
    id: int
    email: EmailStr
    is_admin: bool
    class Config:
        orm_mode = True