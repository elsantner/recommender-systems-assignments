import argparse

import pandas as pd

import movie_data
import colab_recommender
from eval_utils import *


# split the given df into test and train set
# frac ... fraction of entries in training set
def split_into_train_and_test_set(df, frac):
    df_train = df.sample(frac=frac)
    df_test = df.drop(df_train.index)

    return df_train, df_test


def sample_movie_data(md, frac):
    # randomly sample users and movies
    md.user_df = md.user_df.sample(frac=frac)
    md.movies_df = md.movies_df.sample(frac=frac)

    # inner-join ratings with sampled users and movies to remove now invalid entries
    # (i.e. ratings from users or for movies which are not in the sample)
    df_ratings_join_users = pd.merge(md.ratings_df, md.user_df, left_on='UserID', right_on='UserID', how='inner')
    df_join_all = pd.merge(df_ratings_join_users, md.movies_df, left_on='MovieID', right_on='MovieID', how='inner')
    md.ratings_df = df_join_all[['UserID', 'MovieID', 'Rating', 'Timestamp']]


if __name__ == "__main__":
    try:
        # Command line arguments
        # --sample-ratio    set the number of randomly sampled users and movies used in evaluation
        # --k               set the number of nearest neighbours considered
        parser = argparse.ArgumentParser()
        parser.add_argument('--sample-ratio', dest='sample_ratio', type=float, default=1,
                            help='fraction of randomly sampled users and movies used in evaluation (default: 1)')
        parser.add_argument('--k', dest='k', type=int, default=50,
                            help='number of nearest neighbours considered (default: 50)')

        args = parser.parse_args()

        # if sample ratio is out of range
        if args.sample_ratio <= 0 or args.sample_ratio > 1:
            raise ValueError('Sample ratio must be in (0, 1]')

        print('Loading data...')
        movie_data = movie_data.MovieData(path='.././resources/ml-1m')
        # randomly sample data
        sample_movie_data(movie_data, args.sample_ratio)
        # split randomly sampled ratings into training (80%) and test (20%) sets
        df_ratings_train, df_ratings_test = split_into_train_and_test_set(movie_data.ratings_df, 0.8)
        movie_data.ratings_df = df_ratings_train

        # init recommender with training data
        recommender = colab_recommender.ColabRecommender(data=movie_data)

        rating_predictions = []
        df_ratings_by_user = df_ratings_test.groupby('UserID')

        for user_id, group in df_ratings_by_user:
            try:
                print('Generating predictions ... User {0}'.format(user_id))
                predictions = recommender.predict_ratings(user_id, group['MovieID'].tolist(), args.k)

                i = 0
                actual_ratings = group['Rating'].tolist()
                for p in predictions:
                    if p[1] != -1:  # if movie could be rated
                        rating_predictions.append({'user_id': user_id,
                                                   'movie_id': p[0],
                                                   'prediction': p[1],
                                                   'actual': actual_ratings[i]})
                    i += 1
            except ValueError:
                print('\nSkipping user {0} (not in training set)'.format(user_id))

        print('\nResults:')
        print(pd.DataFrame(rating_predictions))

        print('\nMSE: {0}'.format(mae(rating_predictions)))
        print('RMSE: {0}'.format(rmse(rating_predictions)))

    except ValueError as e:
        print('Error: ' + str(e))
    except:
        print('unknown error occurred')
