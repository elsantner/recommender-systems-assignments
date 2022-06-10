import numpy as np


def jaccard_similarity(x, y):
    # convert to set
    a = set(x)
    b = set(y)
    # jaccard = intersection / union
    return float(len(a.intersection(b))) / len(a.union(b))


def dice_coefficient(a, b):
    if not len(a) or not len(b): return 0.0
    """ quick case for true duplicates """
    if a == b: return 1.0
    """ if a != b, and a or b are single chars, then they can't possibly match """
    if len(a) == 1 or len(b) == 1: return 0.0

    """ use python list comprehension, preferred over list.append() """
    a_bigram_list = [a[i:i + 2] for i in range(len(a) - 1)]
    b_bigram_list = [b[i:i + 2] for i in range(len(b) - 1)]

    a_bigram_list.sort()
    b_bigram_list.sort()

    # assignments to save function calls
    lena = len(a_bigram_list)
    lenb = len(b_bigram_list)
    # initialize match counters
    matches = i = j = 0
    while (i < lena and j < lenb):
        if a_bigram_list[i] == b_bigram_list[j]:
            matches += 2
            i += 1
            j += 1
        elif a_bigram_list[i] < b_bigram_list[j]:
            i += 1
        else:
            j += 1

    score = float(matches) / float(lena + lenb)
    return score


def cos_sim(a, b):
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    return dot_product / (norm_a * norm_b)


# filter the movies_df by genre business rules
# return a filtered copy of df
def filter_by_genre_rules(df, mref):
    filtered_df = df.copy()
    return filtered_df[filtered_df['genres'].map(lambda g: are_genres_compatible(g, mref['genres']))]


# implement some business rules for genre compatibility
# return True if genre sets are compatible, otherwise False
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
    # Don't recommend a Drama for a Comedy and vice versa, except if both movies are labelled as {'Comedy', 'Drama'}
    if {'Comedy', 'Drama'}.issubset(union) and not {'Comedy', 'Drama'}.issubset(intersect):
        return False
    return True
