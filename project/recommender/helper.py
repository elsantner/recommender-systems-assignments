def jaccard_similarity(x, y):
    # convert to set
    a = set(x)
    b = set(y)
    # jaccard = intersection / union
    return float(len(a.intersection(b))) / len(a.union(b))
