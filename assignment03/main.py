import argparse
import movie_data
import colab_recommender

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--user', dest='user_id', type=int, help='id of user to generate recommendations for')
        parser.add_argument('--sample', dest='sample_size', type=int, default=-1,
                            help='number of randomly sampled users and movies used in recommendation process (default: use all)')
        parser.add_argument('--k', dest='k', type=int, default=50,
                            help='number of nearest neigbours considered (default: 50)')

        args = parser.parse_args()

        print('Loading data...')
        md = movie_data.MovieData()

        rated_movies = md.get_rated_movies_df(args.user_id).sort_values(by='Rating', ascending=False)[
            ['Title', 'Genres']]
        print('User {0} has previously rated:\n'.format(args.user_id))
        print(rated_movies.head(15))

        print('\nDetermining recommendations...')
        recommender = colab_recommender.ColabRecommender(sample_size=args.sample_size)
        recommended_movies = recommender.get_knn_recommendations(args.user_id, args.k)
        print('Recommendations:\n')
        print(md.get_movie_details(recommended_movies)[['Title', 'Genres']])

    except:
        print('unknown error occurred')