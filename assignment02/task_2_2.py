import pandas as pd

data = [['Toy Story', 21.946943], ['Jumanji', 17.015539], ['Grumpier Old Men', 11.7129]]

# create series
df = pd.DataFrame(data, columns=['title', 'popularity'])
df_sorted = df.sort_values(by='popularity', ascending=True)
print(df_sorted['popularity'].to_string())
