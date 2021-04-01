from flask import Blueprint

cloudapp = Blueprint('cloudapp', __name__)

from app.service import movie
from app.service import user