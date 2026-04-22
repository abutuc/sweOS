import uuid

from pydantic import EmailStr, Field

from app.schemas.base import ApiSchema


class AuthUser(ApiSchema):
    id: uuid.UUID
    email: EmailStr
    full_name: str | None = None


class AuthRegisterRequest(ApiSchema):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str | None = None


class AuthLoginRequest(ApiSchema):
    email: EmailStr
    password: str = Field(min_length=8)


class AuthResponseData(ApiSchema):
    user: AuthUser
    token: str


class AuthEnvelope(ApiSchema):
    data: AuthResponseData
