# Task 5) Finding similar users

import pandas as pd

COMMON_MOVIES_THRESHOLD = 3
df = pd.read_csv('./resources/movies_dataset/ratings_small.csv')

similar_users = []
g_df = df.groupby(['userId'])
selected_user_id = (list(g_df.groups)[0])
# get set of movieIds the first user has rated
rated_movies_of_selected_user = set(g_df.get_group((list(g_df.groups)[0]))['movieId'])
print('User {0} rated movies: {1}'.format(selected_user_id, rated_movies_of_selected_user))

for group_name, df_group in g_df:
    # exclude the selected user ("... find OTHER users users who ...")
    if group_name != selected_user_id and \
            len(rated_movies_of_selected_user.intersection(set(df_group['movieId']))) >= COMMON_MOVIES_THRESHOLD:
        similar_users.append(group_name)

print('Users who rated >= {0} movies User {1} has also rated:\n{2}'
      .format(COMMON_MOVIES_THRESHOLD, selected_user_id, similar_users))
