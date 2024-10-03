from bcrypt import checkpw
from sqlalchemy import String, Integer, Column, Boolean, DateTime

from free_games_email.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    api_key = Column(String, unique=True, nullable=False)
    email_notifications = Column(Boolean, default=False)

    def check_passwd(self, passwd):
        return checkpw(bytes(passwd, 'utf-8'), bytes(self.password, 'utf-8'))


class Game(Base):
    __tablename__ = 'free_games'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    img = Column(String)
