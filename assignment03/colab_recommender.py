# Collaborative recommender implementation
import math
import pandas as pd
import movie_data


class ColabRecommender:
    def __init__(self, data=movie_data.MovieData(), sample_size=-1):
        self.data = data
        self.sample_size = sample_size
        # create pivot table for fast rating lookup
        self.table = self.create_pivot_table()

        # sample random user and movie IDs to reduce computation time
        # the pivot table still contains all data entries, just the ids used in the recommendation process are sampled
        if self.sample_size == -1:
            self.other_user_ids = self.table.columns
            self.movie_ids = self.table.index
        else:
            sample = self.table.sample(self.sample_size, axis='columns')
            self.other_user_ids = sample.columns
            self.movie_ids = sample.sample(sample_size, axis='rows').index

    # create a pivot table (cols: user, rows: movie, cells: rating)
    def create_pivot_table(self):
        return pd.pivot_table(self.data.ratings_df, values='Rating', columns=[self.data.ratings_df['UserID']],
                              index=[self.data.ratings_df['MovieID']])

    # get the mean rating of user_id
    def __get_avg_rating_of_user(self, user_id):
        return self.data.ratings_df.loc[self.data.ratings_df['UserID'] == user_id]['Rating'].mean()

    # get the rating of user_id for movie_id
    # returns NaN if no rating exists
    def __get_rating(self, user_id, movie_id):
        return self.table[user_id][movie_id]

    # get movies rated by both users
    def __get_common_rated_movies(self, user_id1, user_id2):
        common_movies = []
        for element in self.data.ratings_df.loc[self.data.ratings_df['UserID'] == user_id1][
            'MovieID'].drop_duplicates().tolist():
            if element in self.data.ratings_df.loc[self.data.ratings_df['UserID'] == user_id2][
                'MovieID'].drop_duplicates().tolist():
                common_movies.append(element)
        return common_movies

    # returns ((rating for this movie) - (avg rating of user_id))
    def __get_corrected_rating(self, user_id, movie_id):
        return self.__get_rating(user_id, movie_id) - self.__get_avg_rating_of_user(user_id)

    # calculate the pearson correlation between the ratings of user_id1 and user_id2 on commonly rated movies
    def pearson_correlation(self, user_id1, user_id2):
        common_movies = self.__get_common_rated_movies(user_id1, user_id2)

        # not using __get_corrected_rating(...) for better performance (avg only calculated once here)
        avg_rating_user_1 = self.__get_avg_rating_of_user(user_id1)
        avg_rating_user_2 = self.__get_avg_rating_of_user(user_id2)

        numerator = sum([((self.__get_rating(user_id1, movie) - avg_rating_user_1) *
                          (self.__get_rating(user_id2, movie) - avg_rating_user_2))
                         for movie in common_movies])

        rating_squared_sum_sqrt_1 = math.sqrt(sum([pow((self.__get_rating(user_id1, movie) - avg_rating_user_1), 2)
                                                   for movie in common_movies]))
        rating_squared_sum_sqrt_2 = math.sqrt(sum([pow((self.__get_rating(user_id2, movie) - avg_rating_user_2), 2)
                                                   for movie in common_movies]))

        # Returning pearson correlation between both the users.
        denominator = rating_squared_sum_sqrt_1 * rating_squared_sum_sqrt_2

        # avoid div by 0
        if denominator == 0:
            return 0

        return numerator / denominator

    # get the k most similar ("nearest") users to user_id in regard to ratings
    def get_k_nearest_neighbours(self, user_id, k):
        sim_scores = []
        for other_user_id in self.other_user_ids:
            # omit same user
            if other_user_id != user_id:
                sim_scores.append([other_user_id, self.pearson_correlation(user_id, other_user_id)])

        return pd.DataFrame(sim_scores, columns=['userId', 'sim']) \
            .sort_values(by='sim', ascending=False) \
            .head(k)

    # predict the relevance of movie_id considering the ratings of the k nearest neighbours (knn)
    # k ... number of nearest neighbours considered
    # see 'Lecture Slides Part 1', slide 30 for calculation details
    def predict_relevance(self, movie_id, knn, avg_rating_user):
        # calculate predictions for users who rated this movie
        # if user did not rate movie then add 0 to sum (effectively omitting user from calculation)
        numerator = sum(
            [other_user['sim'] * self.__get_corrected_rating(other_user['userId'], movie_id)
             if not math.isnan(self.__get_rating(other_user['userId'], movie_id)) else 0
             for _, other_user in knn.iterrows()])
        denominator = sum([other_user['sim']
                           if not math.isnan(self.__get_rating(other_user['userId'], movie_id)) else 0
                           for _, other_user in knn.iterrows()])

        return avg_rating_user + ((numerator / denominator) if denominator != 0 else 0)

    # generate recommendations
    # see 'Lecture Slides Part 1', slide 33 for details
    def get_knn_recommendations(self, user_id, k=5):
        knn = self.get_k_nearest_neighbours(user_id, k)
        avg_rating_user = self.__get_avg_rating_of_user(user_id)
        already_rated_movies = list(self.data.get_rated_movies_df(user_id)['MovieID'])

        rating_predictions = []
        # predict rating for all movies the given user has NOT yet rated
        for m_id in [m for m in self.movie_ids if m not in already_rated_movies]:
            rating_predictions.append([m_id, self.predict_relevance(m_id, knn, avg_rating_user)])

        df = pd.DataFrame(rating_predictions, columns=['MovieID', 'Relevance'])
        return df.sort_values(by='Relevance', ascending=False).head(20)
