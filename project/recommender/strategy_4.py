from . import helper

RUNTIME_DIFF_NO_PENALTY = 10
RECOMMENDATION_COUNT = 10


# consider runtime diff, language and prod country similarity as well as genre similarity
def calc_sim(row):
    # if one of the factors is 0, retry with one less factor (in order of increasing importance)
    # multiply by 10^n to distinguish results in sorted list (i.e. prefer results with more factors used)
    factor = 1000
    sim = (get_runtime_factor(row['runtime_diff']) * row['lang_sim'] * row['prod_country_sim'] * row['genre_sim']) * factor
    if sim == 0:
        factor = 100
        sim = (get_runtime_factor(row['runtime_diff']) * row['lang_sim'] * row['prod_country_sim']) * factor
        if sim == 0:
            factor = 10
            sim = get_runtime_factor(row['runtime_diff'] * row['lang_sim']) * factor
            if sim == 0:
                factor = 1
                sim = get_runtime_factor(row['runtime_diff']) * factor

    # include popularity ranking to create an order within "categories" of results
    # (i.e. movies with have the same similarity score)
    # adapt to factor used in calculation to avoid high popularity boosting movies
    # which did not fulfill ranking criteria
    return sim + (row['popularity'] * factor * 0.001)


# If the runtime difference if within 'RUNTIME_DIFF_NO_PENALTY', then 1 is returned
# Otherwise, the return value converges to 0 with growing runtime difference
def get_runtime_factor(runtime_diff):
    if runtime_diff <= RUNTIME_DIFF_NO_PENALTY:
        return 1
    return 1 / (runtime_diff - RUNTIME_DIFF_NO_PENALTY)


# currently unused
def calc_cosine_sim(row, mref_runtime):
    v1 = [row['runtime'], row['lang_sim'], row['prod_country_sim']]
    v2 = [mref_runtime, 1, 1]
    return helper.cos_sim(v1, v2)


# Runtime, original language and production countries
# Select movies which have a "similar" runtime (+/- n minutes),
# the same original language and production countries. Rank by popularity.
#
# NOTES:
# A runtime deviation of 10 minutes is accepted without any penalty since such small differences are most likely
# irrelevant to the viewer.
# Genres were included as this strategy (without genres) did not result in meaningful recommendations for en/USA movies.
class RecommenderStrategy4:
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

        # calculate absolute runtime difference
        df['runtime_diff'] = df['runtime'] \
            .apply(lambda r: abs(r - mref['runtime']) if r == r else 9999)

        df['lang_sim'] = df['original_language'].apply(lambda l: l == mref['original_language'])

        df['prod_country_sim'] = df['production_countries'] \
            .apply(lambda c: helper.jaccard_similarity(c, mref['production_countries']) if c == c else 0)

        df['genre_sim'] = df['genres'] \
            .apply(lambda g: helper.jaccard_similarity(g, mref['genres']) if g == g else 0)

        # does not work well: prefers movies with exactly the same runtime
        # df['sim'] = df.apply(lambda row: calc_cosine_sim(row, mref['runtime']), axis=1)

        df['sim'] = df.apply(calc_sim, axis=1)

        return df.sort_values(by='sim', ascending=False).head(self.rec_count)
