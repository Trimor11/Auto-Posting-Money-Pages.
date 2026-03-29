from pydantic import BaseModel, EmailStr


class LoginForm(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = True

    class Config:
        orm_mode = True
