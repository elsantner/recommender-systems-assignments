from . import helper 

RECOMMENDATION_COUNT = 10

def calc_sim(row):
    sim = row['genre_sim'] + row['popularity_sim']
    return sim

# Genres and Popularity
class RecommenderStrategy1:
    def __init__(self, data, sample_size=-1, rec_count=10):
        self.data = data
        self.sample_size = sample_size
        self.rec_count = rec_count

    # recommendations based on genre and popularity
    def get_recommendations(self, mref_id):
        # get reference movie metadata
        mref = self.data.get_movie_metadata_single(mref_id).iloc[0]
        df = self.data.movies_df.copy()
        # remove mref from movie recommendations
        df = df.drop(df[df['id'] == mref_id].index)

        # calculate genre similarity between mref and each movie
        # if a movie has no genres set (if NaN), then set to 0
        df['genre_sim'] = df['genres'] \
            .apply(lambda g: helper.dice_coefficient(g, mref['genres']) if g == g else 0)

        df['popularity_sim'] = df['popularity'] \
            .apply(lambda c: helper.cos_sim(c, mref['popularity']) if c == c else 0)

        df['sim'] = df.apply(calc_sim, axis=1)

        return df.sort_values(by='sim', ascending=False).head(self.rec_count)