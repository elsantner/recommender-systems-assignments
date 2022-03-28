# Task 2.2) Getting used to DataFrames
# Create a nested list as follows: data = [['Toy Story',21.946943],['Jumanji',17.015539],['Grumpier Old Men',11.7129]]
# Create a DataFrame object from the nested list with column headings ‘title’ and ‘popularity’.
# Create a new DataFrame which has the entries sorted by popularity in ascending order.
# Print the popularity values.

import pandas as pd

data = [['Toy Story', 21.946943], ['Jumanji', 17.015539], ['Grumpier Old Men', 11.7129]]

# create series
df = pd.DataFrame(data, columns=['title', 'popularity'])
print(df)
df_sorted = df.sort_values(by='popularity', ascending=True)
print(df_sorted['popularity'].to_string())
