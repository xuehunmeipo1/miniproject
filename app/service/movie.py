from flask import Flask, jsonify, json, request, abort
from app.models.movie import Movie
from app.models.post import Post
from . import cloudapp
from .helper import ExternalService
from app import db
from flask_login import login_required, current_user
from .schema import PostSchema, MovieSchema


@cloudapp.before_app_first_request
def startup():
    ExternalService.initialize_all_movies()


@cloudapp.route('/movies', methods=['GET'])
def get_all_movies():
    # Get all available movies in the local database
    response = dict()
    response['items'] = list()
    for movie in Movie.query.all():
        response['items'].append(movie.to_dict())
    return jsonify(response), 200


@cloudapp.route('/movies/<moviename>', methods=['GET'])
def get_movie_by_name(moviename):
    # Get movies filtered by movie name
    filtered_movie = Movie.query.filter_by(title=moviename).all()
    if filtered_movie:
        response = dict()
        response['items'] = [movie.to_dict() for movie in filtered_movie]
        return jsonify(response), 200
    else:
        # query movie from external api
        if ExternalService.get_movie(moviename):
            return jsonify(
                {'error': 'The movie is not found in the local database, but you can retrieve from external api.'}), 404
        else:
            return jsonify(
                {'error': 'The movie is not found in the local database , and no record in third-party database.'}), 404


@cloudapp.route('/movies/genres/<genre>', methods=['GET'])
def get_movie_by_genres(genre):
    # Get movies filtered by movie genre
    response = dict()
    response['items'] = list()
    movie_list = Movie.query.all()
    for movie in movie_list:
        if genre.lower() in [x.lower() for x in movie.genres.split(",")]:
            response['items'].append(movie.to_dict())
    if response['items']:
        return jsonify(response), 200
    else:
        return {"error": "There is no such genre in the local database."}, 404


@cloudapp.route('/movies', methods=['POST'])
@login_required
def create_new_movie():
    # Add a new movie to the local database by json input
    movie_schema = MovieSchema()
    verify_result = movie_schema.validate(request.json)
    if verify_result:
        return verify_result, 400
    else:
        new_movie = Movie()
        new_movie.set_attr(request.json)
        db.session.add(new_movie)
        db.session.commit()
        return jsonify({"message": "Successfully created a new movie {} in the database".format(new_movie.title)}), 201


@cloudapp.route("/movies/retrieve", methods=['POST'])
@login_required
def retrieve_new_movie():
    # Add a new movie to the local database by calling the third party API
    movie_name = request.json.get("title", "")
    existing_movie = Movie.query.filter_by(title=movie_name)
    if existing_movie.first():
        return jsonify({"error": "The movie is already in your database."}), 404
    if ExternalService.get_movie(movie_name):
        if ExternalService.add_movie(movie_name):
            return jsonify(
                {"message": "Successfully retrieved the movie {} from the database.".format(movie_name)}), 200
        else:
            return jsonify({"error": "Failed to retrieve the movie from third-party database"}), 400
    else:
        return jsonify({"error": "The movie is not found in the third-party database."}), 404


@cloudapp.route('/movies/<moviename>', defaults={'movieid': None}, methods=['DELETE'])
@cloudapp.route('/movies/<moviename>/<movieid>', methods=['DELETE'])
@login_required
def delete_movie(moviename, movieid=None):
    # Delete an existing movie from the local database. If there are movies with same name, return 409.
    # The client need to specify both movie name and movie id if duplicated names exist
    existing_movie = Movie.query.filter_by(title=moviename)
    if existing_movie.first():
        if existing_movie.count() == 1:
            existing_movie.delete()
            db.session.commit()
            return jsonify({"message": "Successfully deleted the movie {} from the database".format(moviename)}), 200
        else:
            existing_movie = Movie.query.filter_by(movie_id=movieid)
            if existing_movie.first():
                existing_movie.delete()
                db.session.commit()
                return jsonify(
                    {"message": "Successfully deleted the movie {} with id {} from the database".format(moviename,
                                                                                                        movieid)}), 200
            else:
                return jsonify(
                    {"error": "There are multiple movies with same specified name. Please specify the movie_id"}), 409
    else:
        return jsonify({"error": "There is no such movie in the database"}), 404


@cloudapp.route('/movies/<moviename>', defaults={'movieid': None}, methods=['PUT'])
@cloudapp.route('/movies/<moviename>/<movieid>', methods=['PUT'])
@login_required
def update_movie(moviename, movieid=None):
    # Update an existing movie in the local database. If there are movies with same name, return 409.
    # The client need to specify both movie name and movie id if duplicated names exist
    existing_movie = Movie.query.filter_by(title=moviename)
    if existing_movie.first():
        if not request.json:
            return jsonify({"error": "The input is not valid."}), 404
        if existing_movie.count() == 1:
            existing_movie.update(dict(request.json))
            db.session.commit()
            return jsonify(
                {"message": "Successfully updated a movie details.", "item": existing_movie.first().to_dict()}), 200
        else:
            existing_movie = Movie.query.filter_by(movieid=movieid)
            if existing_movie.first():
                existing_movie.update(dict(request.json))
                db.session.commit()
                return jsonify(
                    {"message": "Successfully updated a movie details.", "item": existing_movie.first().to_dict()}), 200
            else:
                return jsonify({"message": "There are multiple movies with same specified name"}), 409
    else:
        return jsonify({"error": "There is no such movie in the database"}), 404


@cloudapp.route('/reviews', methods=['POST'])
@login_required
def create_movie_review():
    # add an new movie post
    new_post = Post()
    post_schema = PostSchema()
    verify_result = post_schema.validate(request.json)
    existing_review = Post.query.filter_by(movie_id=request.json.get("movie_id", ""),
                                           user_id=current_user.id)
    if existing_review.first():
        return jsonify({"error": "The review already exists and you can only updated the original review."}), 400
    if verify_result:
        return verify_result, 404
    else:
        new_post.set_attr(request.json)
        new_post.user_id = current_user.id
        db.session.add(new_post)
        db.session.commit()
        return jsonify({"message": "Successfully added a movie review."}), 200


@cloudapp.route('/reviews/collections', methods=['GET'])
@login_required
def get_collections():
    # Get the user's movie reviews
    movie_reviews = Post.query.filter_by(user_id=current_user.id)
    if movie_reviews.first():
        res = dict()
        res['items'] = [review.to_dict() for review in movie_reviews.all()]
        return res, 200
    else:
        return jsonify({"error": "There is no reviews."}), 404


@cloudapp.route('/reviews/collections/<postid>', methods=['PUT'])
@login_required
def update_movie_review(postid):
    # Update an existing movie review
    movie_review = Post.query.filter_by(id=postid)
    if movie_review.first():
        post_schema = PostSchema()
        verify_result = post_schema.validate(request.json)
        if verify_result:
            return verify_result, 400
        movie_review.update(dict(request.json))
        db.session.commit()
        return jsonify(
            {"message": "Successfully updated a movie details.", "item": movie_review.first().to_dict()}), 200
    else:
        return jsonify({"error": "There is no such review."}), 404


@cloudapp.route("/reviews/collections/<postid>", methods=['DELETE'])
@login_required
def remove_movie_review(postid):
    # delete an existing movie review
    movie_review = Post.query.filter_by(id=postid)
    if movie_review.first():
        movie_review.delete()
        db.session.commit()
        return jsonify({"message": "Successfully deleted the review {} from the database".format(postid)}), 200
    else:
        return jsonify({"error": "There is no such review."}), 404
