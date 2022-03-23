import pandas as pd

stats_list = []
df = pd.read_csv('./resources/movies_dataset/ratings_small.csv')

for group_name, df_group in df.groupby(['movieId']):
    stats_list.append({'id': group_name, 'rating_mean': df_group['rating'].mean(),
                      'rating_median': df_group['rating'].median()})

print(stats_list)
