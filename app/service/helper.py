import requests_cache
import requests
from flask import jsonify
from app.models.movie import Movie
from app import db
from flask import current_app

# cache for storing api call
requests_cache.install_cache('movies_api_cache', backend='sqlite', expire_after=36000)
# url to retrieve the top rated movies
request_movie_base_url = "https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language=en-US&page={page}"
# url to retrieve the available movie genres
request_movie_genre_url = "https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}&language=en-US"
# url to retrieve a movie
request_movie_detail_url = "https://api.themoviedb.org/3/search/movie?api_key={api_key}&language=en-US&query={keyword}"


class ExternalService:
    """
    A Class used to provide external service interacted with third-party REST API.
    """

    @staticmethod
    def initialize_all_movies():
        # Retrieve the top rated movies from the third party API.
        for i in range(1, current_app.config['MOVIE_PAGE']):
            current_url = request_movie_base_url.format(api_key=current_app.config['API_KEY'], page=i)
            resp = requests.get(current_url)
            if resp.ok:
                movie_list = resp.json().get("results")
                for movie_object in movie_list:
                    if Movie.query.filter_by(movie_id=movie_object.get("id")).first():
                        continue
                    new_movie = ExternalService.generate_movie_instance(movie_object)
                    db.session.add(new_movie)
                    db.session.commit()

    @staticmethod
    def generate_genres():
        # Generate a dictionary storing the genres id and name retrieved from the third party API.
        resp = requests.get(request_movie_genre_url.format(api_key=current_app.config['API_KEY']))
        if resp.ok:
            genre_list = resp.json().get("genres")
            genre_store = dict()
            for genre in genre_list:
                genre_store[genre.get("id")] = genre.get("name")
            return genre_store
        return dict()

    @staticmethod
    def add_movie(keyword):
        # Retrieve a new movie from the third party API. """
        resp = requests.get(request_movie_detail_url.format(api_key=current_app.config['API_KEY'], keyword=keyword))
        if resp.ok:
            movie_list = resp.json().get("results")
            for movie_object in movie_list:
                if movie_object.get("title") == keyword:
                    new_movie = ExternalService.generate_movie_instance(movie_object)
                    db.session.add(new_movie)
                    db.session.commit()
                    return True
        return False

    @staticmethod
    def get_movie(keyword):
        # Check whether a movie exists in the third party API.
        resp = requests.get(request_movie_detail_url.format(api_key=current_app.config['API_KEY'], keyword=keyword))
        if resp.ok:
            movie_list = resp.json().get("results")
            for movie_object in movie_list:
                if movie_object.get("title") == keyword:
                    return True
        return False

    @staticmethod
    def generate_genre_list(movie):
        # Helper function to convert genres dict to list
        genres_list = ExternalService.generate_genres()
        genres = ','.join(
            str(x) for x in [genres_list.get(genre_id) for genre_id in movie.get("genre_ids")])
        return genres

    @staticmethod
    def generate_movie_instance(movie_object):
        # Helper function to generate a new movie instance
        new_movie = Movie()
        new_movie.title = movie_object.get("title")
        new_movie.movie_id = movie_object.get("id")
        new_movie.score = movie_object.get("vote_average")
        new_movie.release_date = movie_object.get("release_date")
        new_movie.genres = ExternalService.generate_genre_list(movie_object)
        new_movie.description = movie_object.get('overview')
        return new_movie
