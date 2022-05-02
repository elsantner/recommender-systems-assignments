import argparse
import movie_data
import colab_recommender
from eval_utils import *

__MIN_LIKE_THRESHOLD = 3

if __name__ == "__main__":
    try:
        # Command line arguments
        # --sample_frac_users    fraction of randomly sampled users used in evaluation
        # --sample_frac_movies   fraction of randomly sampled movies used in evaluation
        # --k                    set the number of nearest neighbours considered
        parser = argparse.ArgumentParser()
        parser.add_argument('--sample_frac_users', dest='sample_frac_users', type=float, default=1,
                            help='fraction of randomly sampled users used in evaluation (default: 1)')
        parser.add_argument('--sample_frac_movies', dest='sample_frac_movies', type=float, default=1,
                            help='fraction of randomly sampled movies used in evaluation (default: 1)')
        parser.add_argument('--k', dest='k', type=int, default=50,
                            help='number of nearest neighbours considered (default: 50)')
        parser.add_argument('--use_random_predictions', dest='use_random_predictions', type=bool, default=False,
                            help='[TESTING] use random relevance prediction scores (default: False)')

        args = parser.parse_args()

        # if sample ratio is out of range
        if args.sample_frac_users <= 0 or args.sample_frac_users > 1 or \
                args.sample_frac_movies <= 0 or args.sample_frac_movies > 1:
            raise ValueError('Sample fraction must be in (0, 1]')

        print('Loading data...')
        movie_data = movie_data.MovieData(path='resources/ml-1m')
        # randomly sample data
        sample_movie_data(movie_data, args.sample_frac_users, args.sample_frac_movies)

        # TASK 1
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
                # calculate prediction scores ...
                if not args.use_random_predictions:
                    predictions = recommender.predict_ratings(user_id, group['MovieID'].tolist(), args.k)
                # ... or generate random ones if enabled
                else:
                    predictions = get_random_prediction_scores(group['MovieID'].tolist())

                i = 0
                actual_ratings = group['Rating'].tolist()
                for p in predictions:
                    if p[1] != -1:  # if movie could be rated (not part of testing set
                        rating_predictions.append({'user_id': user_id,
                                                   'movie_id': p[0],
                                                   'prediction': p[1],
                                                   'actual': actual_ratings[i]})
                    i += 1
            except ValueError:
                print('\nSkipping user {0} (not in training set)'.format(user_id))

        df_predictions = pd.DataFrame(rating_predictions)

        print('\nResults:')
        print(df_predictions)

        print('\nMSE: {0}'.format(mae(rating_predictions)))
        print('RMSE: {0}'.format(rmse(rating_predictions)))

        true_positives, true_negatives, false_positives, false_negatives = 0, 0, 0, 0

        # TASK 2
        # group prediction list by user
        for user_id, group in df_predictions.groupby('user_id'):
            # sort by prediction desc and take top 10 predictions
            df_pred = group.sort_values(by='prediction', ascending=False).head(10)
            # categorize into relevant/irrelevant movies
            relevant_movies_pred = set(df_pred[df_pred.prediction > __MIN_LIKE_THRESHOLD]['movie_id'].tolist())
            irrelevant_movies_pred = set(df_pred[df_pred.prediction <= __MIN_LIKE_THRESHOLD]['movie_id'].tolist())

            df_actual = group.sort_values(by='actual', ascending=False).head(10)
            relevant_movies_actual = set(df_actual[df_actual.prediction > __MIN_LIKE_THRESHOLD]['movie_id'].tolist())
            irrelevant_movies_actual = set(df_actual[df_actual.prediction <= __MIN_LIKE_THRESHOLD]['movie_id'].tolist())

            # movies in predicted and actual relevant set
            true_positives += len(relevant_movies_actual.intersection(relevant_movies_pred))
            # movies in predicted and actual dislike set
            true_negatives += len(irrelevant_movies_actual.intersection(irrelevant_movies_pred))
            # movies in predicted like but not in actual like set
            false_positives += len(relevant_movies_pred.difference(relevant_movies_actual))
            # movies in predicted like but not in actual like set
            false_negatives += len(irrelevant_movies_pred.difference(irrelevant_movies_actual))

        print('Precision: {0}'.format(precision(true_positives, false_positives)))
        print('Recall: {0}'.format(recall(true_positives, false_negatives)))

    except ValueError as e:
        print('Error: ' + str(e))
    except:
        print('unknown error occurred')
