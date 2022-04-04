import argparse
import movie_data
import colab_recommender


def show_user_id_prompt():
    while True:
        try:
            user_id = int(input("Enter the desired user ID: "))
            return user_id
        except ValueError:
            print("Please input integer only...")


if __name__ == "__main__":
    try:
        # Command line arguments
        # --user        set the user_id for which to generate recommendations
        # --sample      set the number of randomly sampled users and movies used in recommendation process
        # --k           set the number of nearest neighbours considered
        parser = argparse.ArgumentParser()
        parser.add_argument('--user', dest='user_id', type=int, default=-1,
                            help='id of user to generate recommendations for')
        parser.add_argument('--sample', dest='sample_size', type=int, default=-1,
                            help='number of randomly sampled users and movies used in recommendation process (default: use all)')
        parser.add_argument('--k', dest='k', type=int, default=50,
                            help='number of nearest neighbours considered (default: 50)')

        args = parser.parse_args()
        # if user_id was not set via cl arguments then prompt user for input
        if args.user_id == -1:
            args.user_id = show_user_id_prompt()

        print('Loading data...')
        md = movie_data.MovieData()
        # if sample size > actual entry count
        if md.get_movie_count() < args.sample_size or md.get_user_count() < args.sample_size:
            raise ValueError('Sample size must be smaller than user and movie count ({0})'
                             .format(min(md.get_movie_count(), md.get_user_count())))

        # if user_id does not exist
        if not md.check_user_exists(args.user_id):
            raise ValueError('UserID {0} not found'
                             .format(args.user_id))

        # print 15 previously rated movies of selected user (for validation purposes)
        rated_movies = md.get_rated_movies_df(args.user_id).sort_values(by='Rating', ascending=False)[
            ['Title', 'Genres']]
        print('User {0} has previously rated:\n'.format(args.user_id))
        print(rated_movies.head(15))

        # let recommender generate recommendations for selected user
        print('\nDetermining recommendations...')
        recommender = colab_recommender.ColabRecommender(data=md, sample_size=args.sample_size)
        recommended_movies = recommender.get_knn_recommendations(args.user_id, args.k)
        print('Recommendations:\n')
        print(md.get_movie_details(recommended_movies)[['Title', 'Genres']])

    except ValueError as e:
        print('Error: ' + str(e))
    except:
        print('unknown error occurred')
