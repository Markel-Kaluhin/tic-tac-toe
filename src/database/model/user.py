import re
from random import choices
from string import ascii_uppercase, digits

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import validates

from .base import Base

metadata = Base.metadata  # pylint: disable=no-member


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    email = Column(String(50), nullable=True)
    nickname = Column(String(50), nullable=False)
    age = Column(Integer, nullable=True)

    @validates("first_name")
    def validate_first_name(self, key, value):
        if len(value) > 0:
            if not value.istitle():
                raise AssertionError("First name should start from upper case", key)
            if not re.search(r"[A-Za-z]", value):
                raise AssertionError("First name should to only character contain", key)
            return value
        return None

    @validates("last_name")
    def validate_last_name(self, key, value):
        if len(value) > 0:
            if not value.istitle():
                raise AssertionError("Last name should start from upper case", key)
            if not re.search(r"[A-Za-z]", value):
                raise AssertionError("Last name should to only character contain", key)
            return value
        return None

    @validates("email")
    def validate_email(self, key, value):
        if len(value) > 0:
            if not re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", value):
                raise AssertionError('Email is invalid, it should be like "example@example.com"', key)
            return value
        return None

    @validates("nickname")
    def validate_nickname(self, key, value):
        if len(value) == 0:
            return "".join(choices(ascii_uppercase + digits, k=10))
        if re.search(r" +", value):
            raise AssertionError("Nickname shouldn't contain spaces", key)
        return value

    @validates("age")
    def validate_age(self, key, value):
        if len(value) > 0:
            if not str(value).isdigit():
                raise AssertionError("Age is invalid, it should contain digits only", key)
            return int(value)
        return None
