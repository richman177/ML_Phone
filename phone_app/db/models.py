from sqlalchemy import Integer, String, ForeignKey, DateTime
from phone_app.db.database import Base
from typing import Optional, List
from sqlalchemy.orm import Mapped, mapped_column, relationship    
from datetime import datetime 
from passlib.hash import bcrypt 


class UserProfile(Base):
    __tablename__ = 'user_profile'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(32))
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    phone_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    date_registered: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    tokens: Mapped[List['RefreshToken']] = relationship('RefreshToken', back_populates='user',
                                                        cascade='all, delete-orphan')

    def set_passwords(self, password: str):
        self.hashed_password = bcrypt.hash(password)

    def check_password(self, password: str):
        return bcrypt.verify(password, self.hashed_password)

    def __str__(self):
        return self.username


class Phone(Base):
    __tablename__ = 'phone'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rating: Mapped[int] = mapped_column(Integer)
    num_ratings: Mapped[int] = mapped_column(Integer)
    ram: Mapped[int] = mapped_column(Integer)
    rom: Mapped[int] = mapped_column(Integer)
    battery: Mapped[int] = mapped_column(Integer)
    processor: Mapped[Optional[str]] = mapped_column(String,nullable=True)
    front_cam: Mapped[int] = mapped_column(Integer)
    price: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)



class RefreshToken(Base):
    __tablename__ = 'refresh_token'    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    token: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created_data: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user_id: Mapped[int] = mapped_column(ForeignKey('user_profile.id'))
    user: Mapped['UserProfile'] = relationship('UserProfile', back_populates='tokens')    
