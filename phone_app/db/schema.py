from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UserProfileSchema(BaseModel):
    id: int
    first_name: str
    username: str
    password: str
    phone_number: Optional[str]
    age: Optional[int]
    date_registered: datetime


class PhoneSchema(BaseModel):
    rating: int
    num_ratings: int
    ram: int
    rom: int
    battery: int
    front_cam: int

