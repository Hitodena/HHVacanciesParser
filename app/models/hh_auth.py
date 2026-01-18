from typing import Annotated, Literal

from pydantic import BaseModel, EmailStr, Field

from ..custom_types import HHCountryRegions


class EmailAuth(BaseModel):
    email: EmailStr
    password: str = Field(min_length=2)
    answer_req: str | None = None
    auth_type: Literal["email"] = "email"

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "your_password",
                "answer_req": "Hello, I'm a python developer",
                "search_query": "python developer",
                "max_applications": 200,
            }
        }


class PhoneAuth(BaseModel):
    country: HHCountryRegions
    phone: str = Field(pattern=r"^\d{9,12}$")
    password: str = Field(min_length=2)
    answer_req: str | None = None
    auth_type: Literal["phone"] = "phone"

    class Config:
        json_schema_extra = {
            "example": {
                "phone": "291234567",
                "country": "Беларусь",
                "password": "your_password",
                "answer_req": "Hello, I'm a python developer",
                "search_query": "системный аналитик",
                "max_applications": 200,
            }
        }


AuthCredentials = Annotated[
    EmailAuth | PhoneAuth, Field(discriminator="auth_type")
]
