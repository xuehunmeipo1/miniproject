from sqlalchemy import Column, String, Integer
from collections import OrderedDict
from app import db


class Movie(db.Model):
    """
       A Class used to define the Movie object schema.
    """
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(60), nullable=False)
    movie_id = Column(String(50), unique=True)
    score = Column(String(20))
    release_date = Column(String(20))
    genres = Column(String(30))
    description = Column(String(255), nullable=False)

    def to_dict(self):
        res = OrderedDict()
        for key in self.__mapper__.c.keys():
            res[key] = getattr(self, key)
        return res

    def set_attr(self, attrs):
        for k, v in attrs.items():
            if hasattr(self, k) and k != 'id':
                setattr(self, k, v)
