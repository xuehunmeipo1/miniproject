from sqlalchemy import Column, String, Integer
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app import login_manager
import base64


class User(UserMixin, db.Model):
    """
           A Class used to define the User object schema.
    """
    id = Column(Integer, primary_key=True)
    username = Column(String(20), nullable=False, index=True)
    # hashed password as a hidden field
    _hash_password = Column('password', String(128), nullable=False)

    @property
    def password(self):
        return self._hash_password

    @password.setter
    def password(self, plain):
        # hash the password before writing to db
        self._hash_password = generate_password_hash(plain)

    def verify_password(self, plain):
        # method to verify the hashed passwrod correctness
        return check_password_hash(self._hash_password, plain)

    def set_attr(self, attrs):
        for k, v in attrs.items():
            if hasattr(self, k) and k != 'id':
                setattr(self, k, v)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@login_manager.header_loader
def load_user_header(header):
    # Adopt basic auth mechanism for user access management
    header = header.replace('Basic ', '', 1)
    try:
        header = base64.b64decode(header).decode("utf-8").split(":")
        username = header[0]
        password = header[1]
    except TypeError:
        pass
    user = User.query.filter_by(username=username).first()
    if user and user.verify_password(password):
        return user
