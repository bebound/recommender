import statistics

from db_model import *


def get_user_by_id(user_id):
    return User.get(User.id == user_id)


def get_movie_by_id(movie_id):
    return Movie.get(Movie.id == movie_id)


def get_movie_rating_by_user(user_id):
    return list(Rating.select().where(Rating.user_id == user_id))


def get_user_who_rate_movie(movie_id):
    return list(Rating.select().where(Rating.movie_id == movie_id))


def get_user_movie_rating(user_id, movie_id):
    try:
        return Rating.get(Rating.user_id == user_id, Rating.movie_id == movie_id).rating
    except DoesNotExist:
        return 'Unknown'


def get_all_movie():
    return list(Movie.select())


def get_movie_average_rating(movie_id):
    try:
        return AverageRating.get(AverageRating.movie_id == movie_id).rating
    except DoesNotExist:
        return 'Unknown'


def is_user_watched(user, movies):
    """check whether user has wathed movies

    Args:
        user: int user id
        movies: list list of movie ids.
    """
    try:
        Rating.get(Rating.user_id == user, Rating.movie_id << movies)
        return True
    except DoesNotExist:
        return False


def get_user_watched_two_movies(movie1_id, movie2_id):
    """return the user who have watched both movies"""
    a = list(Rating.select(Rating.user_id, fn.COUNT(Rating.movie_id).alias('watched')).where(
        Rating.movie_id << [movie1_id, movie2_id]).group_by(Rating.user_id))
    return [i.user_id for i in a if i.watched == 2]


def get_two_movies_average_rating(movie1_id, movie2_id, threshold=10):
    """return the average rating for two movies, based on the users who have watched both of the movies"""
    users = get_user_watched_two_movies(movie1_id, movie2_id)
    if users and len(users) > threshold:
        ratings1 = Rating.select(Rating.rating).where(Rating.movie_id == movie1_id, Rating.user_id << users)
        ratings2 = Rating.select(Rating.rating).where(Rating.movie_id == movie2_id, Rating.user_id << users)
        return statistics.mean([i.rating for i in ratings1]), statistics.mean([i.rating for i in ratings2])
    else:
        return 0, 0
