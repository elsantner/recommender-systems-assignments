from . import helper


def calc_sim(row):
    sim = row['genre_sim'] + row['director_sim']*1.5 + row['cast_sim']*1.5
    return sim


# Director, cast and genre
class RecommenderStrategy3:
    def __init__(self, data, rec_count=10):
        self.data = data
        self.rec_count = rec_count

    # recommendations based on director, cast and genre
    def get_recommendations(self, mref_id):
        # get reference movie metadata
        mref = self.data.get_movie_metadata(mref_id)
        df = self.data.movies_df.copy()
        # remove mref from movie recommendations
        df = df.drop(df[df['id'] == mref_id].index)

        df['director_sim'] = df['director'] \
            .apply(lambda g: helper.jaccard_similarity(g, mref['director']) if g == g else 0)

        df['cast_sim'] = df['cast'] \
            .apply(lambda c: helper.jaccard_similarity(c, mref['cast']) if c == c else 0)

        df['genre_sim'] = df['genres'] \
            .apply(lambda g: helper.dice_coefficient(g, mref['genres']) if g == g else 0)

        # drop duplicate ids because the dataset has some problems with that
        df = df.loc[df['id'].astype(str).drop_duplicates().index]

        # try to minimize the sequels recommendations by drop all the movies
        # from recommendations that have the same cast
        df = df.loc[df['cast'].astype(str).drop_duplicates().index]

        df['sim'] = df.apply(calc_sim, axis=1)

        return df.sort_values(by='sim', ascending=False).head(self.rec_count)