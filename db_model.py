from peewee import *

db = SqliteDatabase('movie.db')


class User(Model):
    id = IntegerField(primary_key=True)
    gender = CharField()
    age = IntegerField()
    occupation = IntegerField()
    zip_code = CharField()

    class Meta:
        database = db

    def __str__(self):
        return 'User {}, gender: {}, age: {}, occupation: {}, zip_code: {}'.format(self.id, self.gender, self.age,
                                                                                   self.occupation, self.zip_code)


class Movie(Model):
    id = IntegerField(primary_key=True)
    title = CharField()
    genres = CharField()

    class Meta:
        database = db

    def __str__(self):
        return 'Movie {}, title: {}, genres: {}'.format(self.id, self.title, self.genres)


class Rating(Model):
    user_id = IntegerField(index=True)
    movie_id = IntegerField(index=True)
    rating = IntegerField()
    timestamp = IntegerField()

    class Meta:
        database = db

    def __str__(self):
        return 'Rating, user id {}, movie id: {}, rating: {}, timestamp: {}'.format(self.user_id, self.movie_id,
                                                                                    self.rating,
                                                                                    self.timestamp)


class AverageRating(Model):
    movie_id = IntegerField(primary_key=True)
    rating = FloatField()

    class Meta:
        database = db

    def __str__(self):
        return 'Average Rating, movie id: {}, rating {}'.format(self.movie_id, self.rating)
