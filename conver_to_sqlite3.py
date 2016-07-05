import os
import sys
from functools import wraps

from db_api import *


def get_current_path():
    return os.path.dirname(os.path.abspath(__file__))


def parse_user(line):
    row = line.strip().split('::')
    return {'id': int(row[0]), 'gender': row[1], 'age': int(row[2]), 'occupation': int(row[3]), 'zip_code': row[4]}


def parse_movie(line):
    row = line.strip().split('::')
    return {'id': int(row[0]), 'title': row[1], 'genres': row[2]}


def parse_rating(line):
    row = line.strip().split('::')
    return {'user_id': int(row[0]), 'movie_id': int(row[1]), 'rating': int(row[2]), 'timestamp': int(row[3])}


def print_info(func):
    @wraps(func)
    def func_wrapper(cls, filename, parser):
        print('Insert', cls.__name__)
        func(cls, filename, parser)
        print('Finished')

    return func_wrapper


@print_info
def insert(cls, filename, parser):
    current_path = get_current_path()
    rows = []
    with open(os.path.join(current_path, 'ml-1m', filename), encoding="ISO-8859-1") as f:
        for line in f:
            rows.append(parser(line))
    with db.atomic():
        for i in range(0, len(rows), 10000):
            cls.insert_many(rows[i:i + 10000]).execute()


def insert_average():
    print('Insert AverageRating')
    rows = []
    for movie in get_all_movie():
        ratings = []
        for rating in get_user_who_rate_movie(movie):
            ratings.append(rating.rating)
        if len(ratings) > 0:
            rows.append({'movie_id': movie, 'rating': sum(ratings) / len(ratings)})
    with db.atomic():
        for i in range(0, len(rows), 10000):
            AverageRating.insert_many(rows[i:i + 10000]).execute()
    print('Finished')


def main():
    db.connect()
    try:
        db.create_tables([User, Movie, Rating, AverageRating])
    except OperationalError:
        print('Tables already created')
    insert(User, 'users.dat', parse_user)
    insert(Movie, 'movies.dat', parse_movie)
    insert(Rating, 'ratings.dat', parse_rating)
    insert_average()


if __name__ == '__main__':
    sys.exit(main())
