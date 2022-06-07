# 2. Title & Overview TF-IDF
# Rank movies by the similarity of _title_ and _overview_ with _mref_.
# Use Longest Common Subsentence (LCS) for _title_ and TF-IDF for _overview_.
# https://stackoverflow.com/questions/55677314/using-sklearn-how-do-i-calculate-the-tf-idf-cosine-similarity-between-documents/55682395#55682395
from difflib import SequenceMatcher

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from strsimpy.metric_lcs import MetricLCS

RECOMMENDATION_COUNT = 10

def calc_sim(row):
    # works well if enough movies with title_sim > 0 and overview_sim > 0, otherwise many 0 values
    # combine / multiply title similarity and overview similarity
    sim = row['title_sim'] * row['overview_sim']
    return (sim)

metric_lcs = MetricLCS()
def get_similarity_lcs(str1, str2):

    # example for calculation
    # LCS: ABCDEF => length = 6
    # longest = str2 => length = 10
    # => 1 - 6/10 = 0.4
    return(1-metric_lcs.distance(str1, str2))

def get_tf_idf_query_similarity(vectorizer, docs_tfidf, query):
    """
    vectorizer: TfIdfVectorizer model
    docs_tfidf: tfidf vectors for all docs
    query: query doc
    return: cosine similarity between query and all docs
    """

    query_tfidf = vectorizer.transform([query])
    cosineSimilarities = cosine_similarity(query_tfidf, docs_tfidf).flatten()
    # tf-idf: term frequency–inverse document frequency
    # cosine sim: measures the similarity between two vectors
    return cosineSimilarities


# similarity of title (LCS)
class RecommenderStrategy2:
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

 # recommendations based similarity of title
    def get_recommendations(self, mref_id):
        # get reference movie metadata
        mref = self.data.get_movie_metadata_single(mref_id).iloc[0]
        df = self.__sample_movie_df.copy()
        # remove mref from movie recommendations
        df = df.drop(df[df['id'] == mref_id].index)
        # ignore English stopwords (i.e. words that have no significant meaning, i.e. "a", "the", "in", etc.)
        vectorizer = TfidfVectorizer(stop_words='english')
        docs_tfidf = vectorizer.fit_transform(df['overview'].tolist())
        df['title_sim'] = df['title'] \
            .apply(lambda c: get_similarity_lcs(c, mref['title']) if c == c else 0)

        tf_idf_sim = get_tf_idf_query_similarity(vectorizer, docs_tfidf, mref['overview'])
        df['overview_sim'] = tf_idf_sim

        df['sim'] = df.apply(calc_sim, axis=1)

        return df.sort_values(by='sim', ascending=False).head(self.rec_count)

# https://github.com/luozhouyang/python-string-similarity/blob/master/README.md#longest-common-subsequence
# https://medium.com/@ayon_biswas/different-types-of-text-similarity-approaches-9b33f00bed09
# Longest Common SubString (LCS) algorithm considers the maximum length of contiguous chain of characters that exist in both strings.
