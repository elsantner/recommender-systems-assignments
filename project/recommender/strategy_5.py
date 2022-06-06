from . import helper

RELEASE_YEAR_DIFF = 2
RECOMMENDATION_COUNT = 10


# if previous similarity
def calc_sim(row):
    # works well if enough movies with genre_sim > 0 and actor_sim > 0, otherwise many 0 values
    sim = row['genre_sim'] * row['actor_sim']
    if sim == 0:
        # replace 0 values by adding up remaining similarities
        return row['genre_sim'] + row['actor_sim']
    else:
        # add 10 to keep them at the top of the sorted list
        return sim + 10


# Actors, genres and release year
# Select movies within a similar release time frame to mref, e.g. +/- 2 years.
# Sort these movies by actor and genre similarity (using Cosine or Jaccard-based similarity measures).
class RecommenderStrategy5:
    def __init__(self, data, sample_size=-1, rec_count=10):
        self.data = data
        self.sample_size = sample_size
        self.rec_count = rec_count

        # sample random user and movie IDs to reduce computation time
        if self.sample_size == -1:
            # no sampling required
            self.__sample_movie_df = self.data.movies_df
        else:
            self.__sample_movie_df = self.data.movies_df.sample(self.sample_size)

    def get_recommendations(self, mref_id):
        # get reference movie metadata
        mref = self.data.get_movie_metadata_single(mref_id).iloc[0]
        df = self.__sample_movie_df.copy()
        # remove mref from movie recommendations
        df = df.drop(df[df['id'] == mref_id].index)

        mref_release_year = mref['release_year']
        release_filtered_df = df.loc[(df['release_year'] >= mref_release_year - RELEASE_YEAR_DIFF) &
                                     (df['release_year'] <= mref_release_year + RELEASE_YEAR_DIFF)].copy()

        # calculate genre similarity between mref and each movie
        # if a movie has no genres set (if NaN), then set to 0
        release_filtered_df['genre_sim'] = release_filtered_df['genres'] \
            .apply(lambda g: helper.jaccard_similarity(g, mref['genres']) if g == g else 0)

        release_filtered_df['actor_sim'] = release_filtered_df['cast'] \
            .apply(lambda c: helper.jaccard_similarity(c, mref['cast']) if c == c else 0)

        release_filtered_df['sim'] = release_filtered_df.apply(calc_sim, axis=1)

        return release_filtered_df.sort_values(by='sim', ascending=False).head(self.rec_count)
