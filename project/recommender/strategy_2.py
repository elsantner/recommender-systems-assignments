# 2. Title & Overview TF-IDF
# Rank movies by the similarity of _title_ and _overview_ with _mref_.
# Use Longest Common Subsentence (LCS) for _title_ and TF-IDF for _overview_.


RECOMMENDATION_COUNT = 10

# similarity of title (LCS)
class RecommenderStrategy2_1:
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


# similarity of overview (TF-IDF)
class RecommenderStrategy2_2:
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