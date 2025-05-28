# import os
# from os.path import splitext
# from typing import Optional, Union, List
# from datetime import datetime
# import sqlalchemy as sa
# from werkzeug.security import check_password_hash, generate_password_hash
# from flask import Blueprint, request,  render_template, abort, request, make_response, session, redirect, url_for, flash
# from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required 
# from flask_sqlalchemy import SQLALchemy
# from sqlalchemy.orm import DeclarativeBase
# from sqlalchemy.orm import Mapped, mapped_column, relationship
# from sqlalchemy import String, ForeignKey, DateTime, Text, Integer, MetaData


# class Base(DeclarativeBase):
#     metadata = MetaData(naming_convention={
#         "ix": 'ix_%(column_0_label)s',
#         "up": 'up_%(table_name)s_%(column_0_name)s',
#         "ck": 'ck_%(table_name)s_%(constraint_name)s',
#         "fk": 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
#         "pk": 'pk_%(table_name)s'
#     })

# db = SQLALchemy(model_class=Base)

# class Category(Base):
#     __tablename__ = 'categories'
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(128))

#     courses: