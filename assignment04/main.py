import argparse
import movie_data
import content_recommender


def show_user_id_prompt():
    while True:
        try:
            user_id = int(input("Enter the desired user ID: "))
            return user_id
        except ValueError:
            print("Please input integer only...")


def print_user_profile(user_profile):
    sorted_profile = {k: v for k, v in sorted(user_profile.items(), key=lambda item: item[1], reverse=True)}
    for genre in sorted_profile:
        print('{0}: {1}'.format(genre, sorted_profile[genre]))


if __name__ == "__main__":
    try:
        # Command line arguments
        # --user        set the user_id for which to generate recommendations
        # --sample      set the number of randomly sampled movies used in recommendation process
        #               (does not influence user profile creation)
        parser = argparse.ArgumentParser()
        parser.add_argument('--user', dest='user_id', type=int, default=-1,
                            help='id of user to generate recommendations for')
        parser.add_argument('--strategy', dest='strategy', type=str, default='all',
                            help='strategy to use for recommendations (overlap, popularity, count, all)')
        parser.add_argument('--sample', dest='sample_size', type=int, default=-1,
                            help='set the number of randomly sampled movies used in recommendation process (does not '
                                 'influence user profile creation)')

        args = parser.parse_args()
        # if user_id was not set via cl arguments then prompt user for input
        if args.user_id == -1:
            args.user_id = show_user_id_prompt()

        if args.strategy not in ('overlap', 'popularity', 'count', 'all'):
            raise ValueError('Strategy must be in (overlap, popularity, count, all)')

        print('Loading data...')
        md = movie_data.MovieData()
        # if sample size > actual movie count
        if md.get_movie_count() < args.sample_size:
            raise ValueError('Sample size must be smaller than user and movie count ({0})'
                             .format(md.get_movie_count()))

        # create user profile and print
        recommender = content_recommender.ContentBasedRecommender(data=md, sample_size=args.sample_size)
        user_profile = recommender.get_user_profile(args.user_id)
        print('\nUSER PROFILE:')
        print_user_profile(user_profile)

        print('\nGenerating recommendations...')

        # recommendation strategy 1
        if args.strategy in ('overlap', 'all'):
            print('\nRECOMMENDATIONS (OVERLAP):')
            df_recommendations = recommender.get_recommendations_overlap(args.user_id)
            print(df_recommendations[['Title', 'Genres']].head(30))

        # recommendation strategy 2
        if args.strategy in ('popularity', 'all'):
            print('\nRECOMMENDATIONS (POPULARITY):')
            df_recommendations = recommender.get_recommendations_popularity(args.user_id)
            print(df_recommendations[['Title', 'Genres']].head(30))

        # recommendation strategy 3
        if args.strategy in ('count', 'all'):
            print('\nRECOMMENDATIONS (COUNT):')
            df_recommendations = recommender.get_recommendations_count(args.user_id)
            print(df_recommendations[['Title', 'Genres']].head(30))

    except (ValueError, KeyError) as e:
        print('Error: ' + str(e))
    except:
        print('unknown error occurred')
