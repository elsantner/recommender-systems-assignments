from . import helper

# Genres and Popularity
class RecommenderStrategy1:
    def __init__(self, data, rec_count=10):
        self.data = data
        self.rec_count = rec_count

    # recommendations based on genre and popularity
    def get_recommendations(self, mref_id):
        # get reference movie metadata
        mref = self.data.get_movie_metadata(mref_id)
        df = self.data.movies_df.copy()
        # remove mref from movie recommendations
        df = df.drop(df[df['id'] == mref_id].index)

        # calculate genre similarity between mref and each movie
        # if a movie has no genres set (if NaN), then set to 0
        df['genre_sim'] = df['genres'] \
            .apply(lambda g: helper.dice_coefficient(g, mref['genres']) if g == g else 0)

        # take the first 50 movies with the highest sim score and from them clean all the sequels
        df = df.sort_values(by='genre_sim', ascending=False).head(50)
        # sort them by popularity so we can keep the movie from the sequels with the highest popularity
        df = df.sort_values(by='popularity', ascending=False)

        # try to minimize the sequels recommendations by drop all the movies
        # from recommendations that have the same cast
        df = df.loc[df['cast'].astype(str).drop_duplicates().index]

        return df.sort_values(by='genre_sim', ascending=False).head(self.rec_count)
