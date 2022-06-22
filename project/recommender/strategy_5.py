from . import helper
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

RELEASE_YEAR_DIFF = 5

# Tuning:
# Increase release year diff from 2 to 5: more movies for other metrics to work with
# Introduce keyword_sim using TF-IDF: Allows for more fine-grain comparison of the plot in addition to genres sim
# Adjust factor weighting for better results
# Replace multiplicative sim calculation by additive formula: seems to work better for ranking


def calc_sim(row):
    sim = row['keyword_sim'] + row['actor_sim'] + (0.5 * row['genre_sim'])
    return sim + (row['popularity'] * 0.001)


# Return a vector of cosine similarities between docs_tfidf and query
def get_tf_idf_sim(vectorizer, docs_tfidf, query):
    query_tfidf = vectorizer.transform([query])
    return cosine_similarity(query_tfidf, docs_tfidf).flatten()


# Actors, genres and release year
# Select movies within a similar release time frame to mref, e.g. +/- 2 years.
# Sort these movies by actor and genre similarity (using Cosine or Jaccard-based similarity measures).
class RecommenderStrategy5:
    def __init__(self, data, rec_count=10):
        self.data = data
        self.rec_count = rec_count

    def get_recommendations(self, mref_id):
        # get reference movie metadata
        mref = self.data.get_movie_metadata(mref_id)
        df = self.data.movies_df.copy()
        # remove mref from movie recommendations
        df = df.drop(df[df['id'] == mref_id].index)

        # filter out "genre-incompatible" movies
        df = helper.filter_by_genre_rules(df, mref)

        # filter out movies not in the release year threshold
        mref_release_year = mref['release_year']
        release_filtered_df = df.loc[(df['release_year'] >= mref_release_year - RELEASE_YEAR_DIFF) &
                                     (df['release_year'] <= mref_release_year + RELEASE_YEAR_DIFF)].copy()

        # create and fit TF-IDF vectorizer, and create transform for all keywords
        vectorizer = TfidfVectorizer(stop_words='english')
        keywords_tfidf = vectorizer.fit_transform(release_filtered_df['keywords'].tolist())
        release_filtered_df['keyword_sim'] = get_tf_idf_sim(vectorizer, keywords_tfidf, mref['keywords'])

        # calculate genre similarity between mref and each movie
        # if a movie has no genres set (if NaN), then set to 0
        release_filtered_df['genre_sim'] = release_filtered_df['genres'] \
            .apply(lambda g: helper.jaccard_similarity(g, mref['genres']) if g == g else 0)

        release_filtered_df['actor_sim'] = release_filtered_df['cast'] \
            .apply(lambda c: helper.jaccard_similarity(c, mref['cast']) if c == c else 0)

        release_filtered_df['sim'] = release_filtered_df.apply(calc_sim, axis=1)

        return release_filtered_df.sort_values(by='sim', ascending=False).head(self.rec_count)
