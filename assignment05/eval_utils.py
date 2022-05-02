import math
import random

# split the given df into test and train set
# frac ... fraction of entries in training set
import pandas as pd


def split_into_train_and_test_set(df, frac):
    df_train = df.sample(frac=frac)
    df_test = df.drop(df_train.index)

    return df_train, df_test


def sample_movie_data(md, frac_users, frac_movies):
    # randomly sample users and movies
    md.user_df = md.user_df.sample(frac=frac_users)
    md.movies_df = md.movies_df.sample(frac=frac_movies)

    # inner-join ratings with sampled users and movies to remove now invalid entries
    # (i.e. ratings from users or for movies which are not in the sample)
    df_ratings_join_users = pd.merge(md.ratings_df, md.user_df, left_on='UserID', right_on='UserID', how='inner')
    df_join_all = pd.merge(df_ratings_join_users, md.movies_df, left_on='MovieID', right_on='MovieID', how='inner')
    md.ratings_df = df_join_all[['UserID', 'MovieID', 'Rating', 'Timestamp']]


# calculate Mean Absolute Error (MAE)
# rating_predictions ... list of dictionaries containing 'prediction' and 'actual' keys
def mae(rating_predictions):
    sum_of_abs_diff = 0
    for entry in rating_predictions:
        sum_of_abs_diff += abs(entry['prediction'] - entry['actual'])

    return sum_of_abs_diff / len(rating_predictions)


# calculate Root Mean Square Error (RMSE)
# rating_predictions ... list of dictionaries containing 'prediction' and 'actual' keys
def rmse(rating_predictions):
    sum_of_squared_diff = 0
    for entry in rating_predictions:
        sum_of_squared_diff += pow(entry['prediction'] - entry['actual'], 2)

    return math.sqrt(sum_of_squared_diff)


def precision(tp, fp):
    return tp / (tp + fp)


def recall(tp, fn):
    return tp / (tp + fn)


# get rating scores for specific movies
def get_random_prediction_scores(movies_to_rate):
    rating_predictions = []
    # predict rating for movies
    for m_id in movies_to_rate:
        rating_predictions.append([m_id, random.randint(1, 5)])

    return rating_predictions
