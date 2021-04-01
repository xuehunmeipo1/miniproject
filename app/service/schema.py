from marshmallow import Schema, fields, validate
from app.models.post import StatusEnum


class PostSchema(Schema):
    """
       A Class used to define the input schema for a post object.
    """
    movie_id = fields.Number(attribute="movie_id")
    score = fields.Float(attribute="score")
    comment = fields.String(attribute="comment")
    status = fields.String(validate=validate.OneOf([el.value for el in StatusEnum]), required=True, attribute="status")


class MovieSchema(Schema):
    """
       A Class used to define the input schema for a movie object.
    """
    title = fields.String(attribute="title")
    movie_id = fields.Number(attribute="movie_id")
    score = fields.String(attribute="score")
    release_date = fields.String(attribute="release_date")
    genres = fields.String(attribute="genres")
    description = fields.String(attribute="description")
