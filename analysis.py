import math
import random
import sys

from db_api import *
from recommender import average_rating, nearest_neighbour, slope_one, hybrid_algorithm

random.seed(3)

_DEBUG = False
_SAMPLE_NUMBER = 100


def rmsd(a, b):
    """calculate root-mean-square deviation"""
    return math.sqrt(statistics.mean([(i - round(j)) ** 2 for i, j in zip(a, b)]))


def main():
    """calculate RMSD for different recommender algorithm"""
    users = [i.id for i in list(User.select())]
    sample_users = random.sample(users, _SAMPLE_NUMBER)
    actual_result = []
    average_result = []
    nearest_neighbour_result = []
    slope_one_result = []
    hybird_result = []
    for user_id in sample_users:
        print('Current user:', get_user_by_id(user_id))
        movie_id = random.choice(get_movie_rating_by_user(user_id)).movie_id
        print('Current movie:', get_movie_by_id(movie_id))
        actual = get_user_movie_rating(user_id, movie_id)
        print('Actual Rating:', actual)
        actual_result.append(actual)
        avg = average_rating(movie_id, True)
        print('Average Rating:', avg)
        average_result.append(avg)
        nearest = nearest_neighbour(user_id, movie_id, True)
        print('Nearest Neighbour Rating:', nearest)
        nearest_neighbour_result.append(nearest)
        slope = slope_one(user_id, movie_id, True)
        print('Slope One Rating:', slope)
        slope_one_result.append(slope)
        hybrid = hybrid_algorithm(avg, nearest, slope, True)
        print('Hybrid Algorithm Rating:', hybrid)
        if hybrid > 5:
            hybrid = 5
        elif hybrid < 0:
            hybrid = 0
        hybird_result.append(hybrid)
        print()

    if _DEBUG:
        print(actual_result)
        print(average_result)
        print(nearest_neighbour_result)
        print(slope_one_result)
        print(hybird_result)

    print('RMSD of each recommender system')
    print('    Average Rating    '.center(80, '#'))
    print(rmsd(actual_result, average_result))
    print('    Nearest Neighbour    '.center(80, '#'))
    print(rmsd(actual_result, nearest_neighbour_result))
    print('    Slope One    '.center(80, '#'))
    print(rmsd(actual_result, slope_one_result))
    print('    Hybrid Algorithm    '.center(80, '#'))
    print(rmsd(actual_result, hybird_result))


if __name__ == '__main__':
    sys.exit(main())
