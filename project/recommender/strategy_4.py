from . import helper

RUNTIME_DIFF_NO_PENALTY = 10
region_dict = {}

# Tuning:
# Replace language sim with region sim to allow for broader comparison
# Remove runtime as studies have shown it is not important for user similarity rating
# Adjust factor weighting for better results
# Replace multiplicative sim calculation by additive formula: seems to work better for ranking


# consider runtime diff, language and prod country similarity as well as genre similarity
def calc_sim(row):
    sim = (0.5 * row['region_sim']) + (0.1 * row['prod_country_sim']) + row['genre_sim']
    return sim + (row['popularity'] * 0.001)


def init_region_dict():
    for lang in ('ab', 'bg', 'bs', 'hr', 'hu', 'ka', 'mk', 'ro', 'sh', 'sq'):
        region_dict[lang] = 'eastern european'
    for lang in ('eo', 'la'):
        region_dict[lang] = 'special'
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
        df = helper.filter_by_genre_rules(df, mref)

        mref['region'] = get_region(mref)
        df['region'] = df.apply(get_region, axis=1)

        df['region_sim'] = df['region'].apply(lambda l: l == mref['region'])

        df['prod_country_sim'] = df['production_countries'] \
            .apply(lambda c: helper.jaccard_similarity(c, mref['production_countries']) if c == c else 0)

        df['genre_sim'] = df['genres'] \
            .apply(lambda g: helper.jaccard_similarity(g, mref['genres']) if g == g else 0)

        df['sim'] = df.apply(calc_sim, axis=1)

        return df.sort_values(by='sim', ascending=False).head(self.rec_count)
