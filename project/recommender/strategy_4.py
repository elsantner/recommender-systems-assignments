from . import helper

RUNTIME_DIFF_NO_PENALTY = 10

region_dict = {}


# Tuning:
# Replace language sim with region sim to allow for broader comparison
# Remove runtime as studies have shown it is not important for user similarity rating
# Adjust factor weighting for better results


# consider runtime diff, language and prod country similarity as well as genre similarity
def calc_sim(row):
    # if one of the factors is 0, retry with one less factor (in order of increasing importance)
    # multiply by 10^n to distinguish results in sorted list (i.e. prefer results with more factors used)
    factor = 1000
    sim = (row['region_sim'] * (0.2 * row['prod_country_sim']) * row['genre_sim']) * factor
    if sim == 0:
        factor = 100
        sim = (row['region_sim'] * (0.2 * row['prod_country_sim'])) * factor
        if sim == 0:
            factor = 10
            sim = row['region_sim'] * factor

    # include popularity ranking to create an order within "categories" of results
    # (i.e. movies with have the same similarity score)
    # adapt to factor used in calculation to avoid high popularity boosting movies
    # which did not fulfill ranking criteria
    return sim + (row['popularity'] * factor * 0.0005)


def init_region_dict():
    for lang in ('ab', 'bg', 'bs', 'hr', 'hu', 'ka', 'mk', 'ro', 'sh', 'sq'):
        region_dict[lang] = 'eastern european'
    for lang in ('eo', 'la'):
        region_dict[lang] = 'artificial'
    for lang in ('ca', 'el', 'es', 'eu', 'fr', 'gl', 'it', 'pt', 'ay', 'qu'):
        region_dict[lang] = 'latin'
    for lang in ('et', 'fi', 'is', 'iu', 'lt', 'lv', 'nb', 'no', 'sv'):
        region_dict[lang] = 'northern european'
    for lang in ('cs', 'da', 'de', 'fy', 'lb', 'nl', 'pl'):
        region_dict[lang] = 'central european'
    for lang in ('af', 'am', 'bm', 'rw', 'wo', 'zu'):
        region_dict[lang] = 'african'
    for lang in ('ar', 'fa', 'he', 'hy', 'ku', 'mt', 'ps', 'tg', 'tr'):
        region_dict[lang] = 'middle eastern'
    for lang in (
            'bn', 'bo', 'cn', 'hi', 'kn', 'lo', 'ml', 'mn', 'mr', 'ms', 'ne', 'pa', 'si', 'ta', 'te', 'th', 'ur', 'vi',
            'zh'):
        region_dict[lang] = 'central asian'
    for lang in ('ja', 'ko'):
        region_dict[lang] = 'korea/japan'
    for lang in ('id', 'jv', 'sm', 'tl'):
        region_dict[lang] = 'pacific'
    for lang in ('kk', 'ky', 'ru', 'sl', 'sk', 'sr', 'uk', 'uz'):
        region_dict[lang] = 'slavic'
    for lang in ('en', 'cy'):
        region_dict[lang] = 'english'
    region_dict['xx'] = 'no language'


def get_region(row):
    if row['original_language'] != row['original_language']:
        return 'unknown'
    return region_dict[row['original_language']]


def filter_by_genre_rules(df, mref):
    filtered_df = df.copy()
    return filtered_df[filtered_df['genres'].map(lambda g: are_genres_compatible(g, mref['genres']))]


# implement some business rules for genre compatibility
def are_genres_compatible(g1, g2):
    # avoid NaN values
    if g1 != g1:
        g1 = {}
    if g2 != g2:
        g2 = {}
    intersect = set(g1).intersection(set(g2))
    union = set(g1).union(set(g2))
    # only recommend Family movies if mref is a Family movie
    if 'Family' in union and 'Family' not in intersect:
        return False
    # Don't recommend a Drama for a Comedy and vice versa, except if both movies are labelled as both
    if {'Comedy', 'Drama'}.issubset(union) and not {'Comedy', 'Drama'}.issubset(union):
        return False
    return True


# Runtime, original language and production countries
# Select movies which have a "similar" runtime (+/- n minutes),
# the same original language and production countries. Rank by popularity.
#
# NOTES:
# A runtime deviation of 10 minutes is accepted without any penalty since such small differences are most likely
# irrelevant to the viewer.
# Genres were included as this strategy (without genres) did not result in meaningful recommendations for en/USA movies.
class RecommenderStrategy4:
    def __init__(self, data, rec_count=10):
        self.data = data
        self.rec_count = rec_count
        init_region_dict()

    def get_recommendations(self, mref_id):
        # get reference movie metadata
        mref = self.data.get_movie_metadata_single(mref_id).iloc[0]
        df = self.data.movies_df.copy()
        # remove mref from movie recommendations
        df = df.drop(df[df['id'] == mref_id].index)

        # filter out "genre-incompatible" movies
        df = filter_by_genre_rules(df, mref)

        mref['region'] = get_region(mref)
        df['region'] = df.apply(get_region, axis=1)

        df['region_sim'] = df['region'].apply(lambda l: l == mref['region'])

        df['prod_country_sim'] = df['production_countries'] \
            .apply(lambda c: helper.jaccard_similarity(c, mref['production_countries']) if c == c else 0)

        df['genre_sim'] = df['genres'] \
            .apply(lambda g: helper.jaccard_similarity(g, mref['genres']) if g == g else 0)

        df['sim'] = df.apply(calc_sim, axis=1)

        return df.sort_values(by='sim', ascending=False).head(self.rec_count)
