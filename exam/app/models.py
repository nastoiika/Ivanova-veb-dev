from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text, Integer, MetaData
from flask_login import UserMixin
from datetime import datetime
from typing import Optional
from werkzeug.security import check_password_hash, generate_password_hash

class Base(DeclarativeBase):
  metadata = MetaData(naming_convention={
        "ix": 'ix_%(column_0_label)s',
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    })

db = SQLAlchemy(model_class=Base)

class Role(Base):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text(300))

    users: Mapped[list["User"]] = relationship("User", back_populates="role")

class User(Base, UserMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    middle_name: Mapped[Optional[str]] = mapped_column(String(100))
    login: Mapped[str] = mapped_column(String(100), unique=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))

    role: Mapped["Role"] = relationship("Role", back_populates="users")
    adoptions: Mapped[list["Adoption"]] = relationship("Adoption", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Animal(Base):
    __tablename__ = 'animals'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text(300))
    age: Mapped[int] = mapped_column(Integer)
    breed: Mapped[str] = mapped_column(String(100))
    gender: Mapped[str] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(100), default='available')
    arrival_date: Mapped[datetime] = mapped_column(default=datetime.now)

    photos: Mapped[list["Photo"]] = relationship("Photo", back_populates="animal", cascade="all, delete-orphan")
    adoptions: Mapped[list["Adoption"]] = relationship("Adoption", back_populates="animal", cascade="all, delete-orphan")

class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    mime: Mapped[str] = mapped_column(String(100))

    animal_id: Mapped[int] = mapped_column(ForeignKey("animals.id"))
    animal: Mapped[Animal] = relationship("Animal", back_populates="photos")
   
class Adoption(Base):
    __tablename__ = "adoptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(default=datetime.now)
    status: Mapped[str] = mapped_column(String(100))
    contact_details: Mapped[str] = mapped_column(String(100))

    animal_id: Mapped[int] = mapped_column(ForeignKey("animals.id"))
    animal: Mapped[Animal] = relationship("Animal", back_populates="adoptions")

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship("User", back_populates="adoptions")
