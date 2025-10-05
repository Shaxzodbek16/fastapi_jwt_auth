import re

from pydantic import BaseModel, Field, field_validator
from fastapi import HTTPException


class LoginSchema(BaseModel):
    email: str = Field(..., examples=["example@gmail.com"], max_length=255)
    password: str = Field(..., min_length=8, examples=["Strongpassword1@"])


class RegisterSchema(LoginSchema):
    first_name: str = Field(..., min_length=2, max_length=255)
    last_name: str | None = Field(None, min_length=2, max_length=255)
    code: int = Field(
        ..., description="User code for registration", examples=[123456, 654321]
    )

    @field_validator("email")
    def validate_email(cls, v):
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise HTTPException(400, "Invalid email address")
        return v.lower()

    @field_validator("password")
    def validate_password(cls, v):
        if (
            len(v) < 8
            or not re.search(r"[A-Z]", v)
            or not re.search(r"[a-z]", v)
            or not re.search(r"[0-9]", v)
            or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v)
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Password must be at least 8 characters long and include at least "
                    "one uppercase letter, one lowercase letter, one number, and one special character."
                ),
            )
        return v


class TokenBlokeSchema(BaseModel):
    refresh_token: str


class TokenResponseSchema(TokenBlokeSchema):
    access_token: str
    token_type: str = "Bearer"
