import pandas as pd

from . import data_utils


def pearson(row1, row2):
    # create matrix of 2 row entries (compare 2 users)
    df = pd.concat([row1, row2], axis=1, keys=['user1', 'user2'])

    count = 0

    # check how many movies the two users have in common
    for i in df.index:
        if df['user1'][i] >= 0 and df['user2'][i] >= 0:
            count += 1
        if count >= 3:
            break

    # assume that only if there are at least three movies in common the two users are neighbors
    if count >= 3:
        # calculate pearson correlation
        corr = df.corr(method="pearson", min_periods=1)
        return corr['user1']['user2']
    else:
        # set correlation to nan if there are not enough common movies
        return 'nan'


def create_user_item_matrix(movie_ratings):
    # create the pivot table with user ids and movie ids as axes and ratings as values
    return pd.pivot_table(movie_ratings, index=['userId'], columns=['movieId'], values=['rating'])


# generate knn recommendations
def get_recommendations(movie_ratings, user_items, user_id, k, exclude_already_rated=False):
    # if user "does not exist" (or is not loaded in sample), return
    try:
        user_items.loc[user_id]
    except KeyError:
        return []

    # get all ids from the movies that our user has rated
    movie_ids = movie_ratings[(movie_ratings.userId == user_id)]['movieId'].to_list()
    print('\nUser {0} has rated'.format(str(user_id)))
    print(movie_ids)

    # calculate the correlation between the selected user and all the other users
    user_similarities = []
    i = 0
    for index, row in user_items.iterrows():
        dictEntry = {'id''': index + 1, 'similarity': pearson(user_items.loc[user_id], user_items.iloc[i])}
        user_similarities.append(dictEntry)
        i += 1

    # filter users with NaN similarity and the user themselves
    user_similarities = [x for x in user_similarities if str(x['similarity']) != 'nan' and x['id'] != user_id]

    # sort the list to start with the most similar users
    user_similarities = sorted(user_similarities, key=lambda k: k["similarity"], reverse=True)
    print('\nMost similar users:')
    print(user_similarities)

    # starting point for concatenated dataframes
    combinedDF = pd.DataFrame(columns=['movieId', 'rating'])

    # k = min(numNeighbors, <num users>)
    if len(user_similarities) < k:
        k = len(user_similarities)

    # concat all the dataframes from the similar users
    # df then contains all ratings of similar users
    for i in range(k):
        simID = user_similarities[i]["id"]
        combinedDF = pd.concat([combinedDF, movie_ratings[(movie_ratings.userId == simID)]])

    # only use movie_id and rating (other things are not necessary), and group by movie_id
    smallCombinedDF = combinedDF[['movieId', 'rating']].copy().groupby(by='movieId')

    # calculate the mean of each movie that was in the rating list
    # of similar users and store it in a list of dictionaries
    recommendedMovies = []
    for name, group in smallCombinedDF:
        dictRatingEntry = {"movieId": name, "mean_rating": group.mean().rating}
        recommendedMovies.append(dictRatingEntry)

    # sort the recommended movies by their mean rating
    recommendedMovies = sorted(recommendedMovies, key=lambda k: k["mean_rating"], reverse=True)

    # check if the selected user has not seen the movie yet that is getting recommended to him
    if exclude_already_rated:
        recommendedMoviesCorrected = []
        for m in recommendedMovies:
            if m["movieId"] not in movie_ids:
                dictIntersected = {"movieId": m["movieId"], "mean_rating": m["mean_rating"]}
                recommendedMoviesCorrected.append(dictIntersected)

        recommendedMovies = recommendedMoviesCorrected

    # return only the top-20 recommendations
    return recommendedMovies[:20]
