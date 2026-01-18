from typing import Annotated, Literal

from pydantic import BaseModel, EmailStr, Field, SecretStr

from ..custom_types import HHCountryRegions


class EmailAuth(BaseModel):
    email: EmailStr
    password: SecretStr = Field(min_length=2)
    auth_type: Literal["email"] = "email"


class PhoneAuth(BaseModel):
    country: HHCountryRegions
    phone: str = Field(pattern=r"^\d{9,12}$")
    password: SecretStr = Field(min_length=2)
    auth_type: Literal["phone"] = "phone"


AuthCredentials = Annotated[
    EmailAuth | PhoneAuth, Field(discriminator="auth_type")
]
