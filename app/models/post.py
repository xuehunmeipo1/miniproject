from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app import db
from collections import OrderedDict
import enum
from datetime import datetime


class StatusEnum(enum.Enum):
    """
           A Class used to define enum values for post status.
     """
    Watched = "Watched"
    Collected = "Collected"


class Post(db.Model):
    """
          A Class used to define the Post object schema.
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    user = relationship('User')
    movie = relationship('Movie')
    user_id = Column(Integer, ForeignKey('user.id'))
    movie_id = Column(Integer, ForeignKey('movies.id'))
    score = Column(String(20))
    comment = Column(String(255), nullable=False)
    status = Column(Enum(StatusEnum, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    created_on = Column(DateTime(), default=datetime.utcnow)
    updated_on = Column(DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_attr(self, attrs):
        for k, v in attrs.items():
            if hasattr(self, k) and k != 'id':
                setattr(self, k, v)

    def to_dict(self):
        res = OrderedDict()
        for key in self.__mapper__.c.keys():
            # handle enum attribute conversion
            if key == 'status':
                res[key] = getattr(self, key).value
            else:
                res[key] = getattr(self, key)
        return res
