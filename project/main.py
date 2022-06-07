import argparse

import pandas as pd

import movie_data
from recommender.strategy_4 import RecommenderStrategy4
from recommender.strategy_5 import RecommenderStrategy5
from recommender.strategy_1 import RecommenderStrategy1
from recommender.strategy_2 import RecommenderStrategy2


RECOMMENDATION_COUNT = 10


def show_movie_id_prompt():
    while True:
        try:
            movie_id = int(input("Enter the movie ID: "))
            return movie_id
        except ValueError:
            print("Please input integer only...")


def validate_args(m_data, arguments):
    if args.strategy not in ('all', '1', '2', '3', '4', '5'):
        raise ValueError('Strategy must be in (all, 1-5)')

    # if sample size > actual movie count
    if m_data.get_movie_count() < arguments.sample_size:
        raise ValueError('Sample size must be smaller than user and movie count ({0})'
                         .format(m_data.get_movie_count()))
    if not m_data.movie_exists(arguments.movie_id):
        raise ValueError('Movie {0} does not exist'.format(arguments.movie_id))


if __name__ == "__main__":
    # try:

    # Command line arguments
    # --user        set the user_id for which to generate recommendations
    # --strategy    strategy to be used in recommendation process
    # --sample      set the number of randomly sampled movies used in recommendation process
    #               (does not influence user profile creation)
    parser = argparse.ArgumentParser()
    parser.add_argument('--movie', dest='movie_id', type=int, default=-1,
                        help='id of the reference movie')
    parser.add_argument('--strategy', dest='strategy', type=str, default='all',
                        help='strategy to use for recommendations (1-5)')
    parser.add_argument('--sample', dest='sample_size', type=int, default=-1,
                        help='set the number of randomly sampled movies used in recommendation process')

    args = parser.parse_args()
    # if movie_id was not set via cl arguments then prompt user for input
    if args.movie_id == -1:
        args.movie_id = show_movie_id_prompt()

    print('Loading data...')
    md = movie_data.MovieData()

    validate_args(md, args)

    print('\nGenerating recommendations...')

    # Please Note: How to access list in dataframe cells
    # print(row['cast'][0][i])   ...  where 'cast' is the column name and 'i' is the index within the embedded list

    # auto-adapt df table size to console window
    pd.options.display.width = 0

    # Use 'args.movie_id' and 'md' to generate recommendations
    # recommendation strategy 1
    if args.strategy in ('1', 'all'):
        print('\nReference movie:')
        print(md.get_movie_metadata_single(args.movie_id)[['id', 'title', 'popularity', 'genres', 'cast']])

        print('\nRECOMMENDATIONS (1):')
        rec = RecommenderStrategy1(data=md, sample_size=args.sample_size, rec_count=RECOMMENDATION_COUNT)
        recommendations1 = rec.get_recommendations(args.movie_id)
        # sort the top 10 recommendations of genre by their popularity
        recommendations1 = recommendations1.sort_values(by='popularity', ascending=False)
        print(recommendations1[['id', 'title', 'popularity', 'genres', 'cast', 'sim']])

    if args.strategy in ('2', 'all'):
        print('\nReference movie:')
        print(md.get_movie_metadata_single(args.movie_id)[['id', 'title', 'overview', 'genres']])

        print('\nRECOMMENDATIONS (2):')
        rec = RecommenderStrategy2(data=md, sample_size=args.sample_size, rec_count=RECOMMENDATION_COUNT)
        recommendations2 = rec.get_recommendations(args.movie_id)
        print(recommendations2[['id', 'title', 'overview', 'sim', 'genres']])

    # recommendation strategy 3
    if args.strategy in ('3', 'all'):
        print('\nRECOMMENDATIONS (3):')
        # TODO: implement recommendation strategy 3
    # recommendation strategy 4
    if args.strategy in ('4', 'all'):
        print('\nReference movie:')
        print(md.get_movie_metadata_single(args.movie_id)[['id', 'title', 'runtime', 'original_language',
                                                           'production_countries', 'genres']])

        print('\nRECOMMENDATIONS (4):')
        rec = RecommenderStrategy4(data=md, sample_size=args.sample_size, rec_count=RECOMMENDATION_COUNT)
        recommendations4 = rec.get_recommendations(args.movie_id)
        print(recommendations4[['id', 'title', 'runtime', 'original_language', 'production_countries', 'genres', 'sim']])
    # recommendation strategy 5
    if args.strategy in ('5', 'all'):
        print('\nReference movie:')
        print(md.get_movie_metadata_single(args.movie_id)[['id', 'title', 'release_year', 'genres', 'cast']])

        print('\nRECOMMENDATIONS (5):')
        rec = RecommenderStrategy5(data=md, sample_size=args.sample_size, rec_count=RECOMMENDATION_COUNT)
        recommendations5 = rec.get_recommendations(args.movie_id)
        print(recommendations5[['id', 'title', 'release_year', 'genres', 'cast', 'sim']])

    # TODO: reactive error handling once development/debugging is finished
    # except (ValueError, KeyError) as e:
    #    print('Error: ' + str(e))
