from . import helper

RECOMMENDATION_COUNT = 10

def calc_sim(row):
    if row['director_sim'] >= 0.9 and row['genre_sim'] > 0.5:
        sim = row['director_sim'] + row['genre_sim']
        return sim
    elif row['cast_sim'] >= 0.5 and row['genre_sim'] > 0.5:
        sim = row['cast_sim'] + row['genre_sim']
        return sim
    else:
        sim = row['genre_sim']
        return sim


# Genres and Popularity
class RecommenderStrategy3:
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
        df['director_sim'] = df['director'] \
            .apply(lambda g: helper.jaccard_similarity(g, mref['director']) if g == g else 0)

        df['cast_sim'] = df['cast'] \
            .apply(lambda c: helper.jaccard_similarity(c, mref['cast']) if c == c else 0)

        df['genre_sim'] = df['genres'] \
            .apply(lambda g: helper.dice_coefficient(g, mref['genres']) if g == g else 0)

        df['sim'] = df.apply(calc_sim, axis=1)

        return df.sort_values(by='sim', ascending=False).head(self.rec_count)