from pydantic import BaseModel, EmailStr, Field, SecretStr

from ..custom_types import HHCountryRegions


class EmailAuth(BaseModel):
    email: EmailStr
    password: SecretStr = Field(min_length=2)


class PhoneAuth(BaseModel):
    country: HHCountryRegions
    phone: str = Field(pattern=r"^\d{9,12}$")
    password: SecretStr = Field(min_length=2)


AuthCredentials = EmailAuth | PhoneAuth
