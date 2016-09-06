import math
import sys

from scipy.spatial.distance import pdist

from db_api import *

_DEBUG = False
_NEAREST_NUMBER = 15


def print_user_info(user_id):
    print(get_user_by_id(user_id))


def print_movie_info(movie_id):
    print(get_movie_by_id(movie_id))


def print_actual_rating(user_id, movie_id):
    print('The actual rating is', get_user_movie_rating(user_id, movie_id))


def average_rating(movie_id, silence=False):
    """average rating of movie"""
    mean_rating = statistics.mean([i.rating for i in get_user_who_rate_movie(movie_id)])
    if not silence:
        print('    Average Rating    '.center(80, '#'))
        print(round(mean_rating), '(', mean_rating, ')')
    return mean_rating


def custom_distance(a, b):
    """calculate distance between two list by custom way"""
    return sum([abs(i - j) ** 2 for (i, j) in zip(a, b)]) / len(a)


def cosine_distance(a, b):
    """calculate cosine distance for two list"""
    return pdist([a, b], 'cosine')


def canberra_distance(a, b):
    """calculate canberra distance for two list"""
    return pdist([a, b], 'canberra')


def count_info(neighbours):
    """print some distribution information for neighbours"""
    count_common = {}
    count_rating = {}
    for i in neighbours:
        if i[3] not in count_common:
            count_common[i[3]] = 1
        else:
            count_common[i[3]] += 1
        if i[1] not in count_rating:
            count_rating[i[1]] = 1
        else:
            count_rating[i[1]] += 1

    print(count_common)
    print(count_rating)
    print(statistics.mean([i[1] for i in neighbours]))


def similarity(candidate, user):
    """calculate the similarity of candidate based on ratings

    Args:
        candidate: dict {movie_id:rating}
        user: dict {movie_id:rating}

    Return:
        list: (user_id, rating, distance, common_movie)
    """
    candidate_rating_vector = []
    user_rating_vector = []
    for i in candidate:
        if i in user:
            candidate_rating_vector.append(candidate[i])
            user_rating_vector.append(user[i])

    ratio = math.log(30 + len(user_rating_vector), 64)
    return [candidate['user_id'], candidate['target_rating'],
            custom_distance(candidate_rating_vector, user_rating_vector) / ratio,
            len(user_rating_vector)]


def get_similar_user(user_id, movie_id):
    candidates = {}
    neighbours = []
    user_watched = {}

    current_user = {i.movie_id: i.rating for i in get_movie_rating_by_user(user_id)}
    if _DEBUG:
        print('This user has rated', len(get_movie_rating_by_user(user_id)), 'movies')

    user_watched = {i.user_id: i.movie_id for i in get_user_who_rate_movie(movie_id)}
    if _DEBUG:
        print(len(user_watched), 'users have watched this movie')

    for user in user_watched:
        # user who watched target movie
        if is_user_watched(user, list(current_user.keys())):
            # user who wathed target movie and has common movie with target user
            for rating in get_movie_rating_by_user(user):
                candidates.setdefault(rating.user_id, {})[rating.movie_id] = rating.rating
                candidates.setdefault(rating.user_id, {})['user_id'] = rating.user_id
                if rating.movie_id == movie_id:
                    candidates.setdefault(rating.user_id, {})['target_rating'] = rating.rating

    for candidate in candidates:
        neighbours.append(similarity(candidates[candidate], current_user))

    neighbours = list(filter(lambda x: not (x[2] == 0 and x[3] <= 5), neighbours))
    neighbours.sort(key=lambda x: x[2])

    if _DEBUG:
        count_info(neighbours[1:_NEAREST_NUMBER + 1])
    return neighbours[1:_NEAREST_NUMBER + 1]


def calculate_neighbour_rating(neighbours):
    """return predict score based on neighbour

    Args:
        neighbours: list (user_id, rating, distance, common_movie)

    Return:
        score: int
    """
    total_weight = 0
    total_score = 0
    if _DEBUG:
        for i in neighbours:
            print(i[1], i[2], i[3])
    for i, user in enumerate(neighbours):
        total_weight += 1 / math.log(2 + i, len(neighbours))
        total_score += user[1] / math.log(2 + i, len(neighbours))
    return total_score / total_weight


def nearest_neighbour(user_id, movie_id, silence=False):
    """use nearest neighbour to recommend"""
    neighbours = get_similar_user(user_id, movie_id)
    predict_value = calculate_neighbour_rating(neighbours)
    if not silence:
        print('    Nearest Neighbour    '.center(80, '#'))
        print(round(predict_value), '(', predict_value, ')')
    return predict_value


def get_movie_genres(movie_id):
    return get_movie_by_id(movie_id).genres.split('|')


def genres_similarity(movie_id, genres):
    count = 0
    for i in get_movie_genres(movie_id):
        if i in genres:
            count += 1
    return count


def parse_result(a):
    if a > 5.5:
        a = 5.5
    elif a < -0.5:
        a = -0.5
    return a


def slope_one(user_id, movie_id, silence=False):
    """use slope one algorithm to recommend"""
    watched_movies = [i.movie_id for i in get_movie_rating_by_user(user_id)]
    watched_movies.remove(movie_id)
    target_genres = get_movie_genres(movie_id)

    predict_ratings = []

    for movie in watched_movies:
        if genres_similarity(movie, target_genres):
            user_rating = get_user_movie_rating(user_id, movie)
            movie_rating, target_movie_rating, weight = get_two_movies_average_rating(movie, movie_id)
            if weight != 0:
                guess_rating = user_rating + movie_rating - target_movie_rating
                for i in range(weight):
                    predict_ratings.append(parse_result(guess_rating))
    if predict_ratings:
        predict_value = statistics.mean(predict_ratings)
    else:
        predict_value = average_rating(movie_id, True)

    if not silence:
        print('    Slope One    '.center(80, '#'))
        print(round(predict_value), '(', predict_value, ')')
    return predict_value


def hybrid_algorithm(avg, nearest, slope, silence=False):
    """hybrid algorithm based on average rating, nearest neighbour and slope one

    I don't use slope one because it's hard to find the similar movie, so the performance
    of slope one is poor.
    """
    sign = (nearest - avg) / abs(nearest - avg)
    ratio = 0.2
    predict_value = nearest + sign * abs(nearest - avg) * ratio
    if not silence:
        print('    Hybrid Algorithm    '.center(80, '#'))
        print(round(predict_value), '(', predict_value, ')')
    return predict_value


def predict(user_id, movie_id):
    """use different algorithm to predict movie rating"""
    print_user_info(user_id)
    print_movie_info(movie_id)
    print_actual_rating(user_id, movie_id)
    avg = average_rating(movie_id)
    nearest = nearest_neighbour(user_id, movie_id)
    slope = slope_one(user_id, movie_id)
    hybrid_algorithm(avg, nearest, slope)


def main():
    print('Predict movie rating')
    while True:
        try:
            user_id = int(input('\nPlease input user id:'))
            movie_id = int(input('please input movie id:'))
            predict(user_id, movie_id)
        except DoesNotExist:
            print('User/Movie does not exist, try again')


if __name__ == '__main__':
    sys.exit(main())
