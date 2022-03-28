# Task 2.1) Getting used to Series
# Create a list of strings as follows: data = ['Toy Story','Jumanji','Grumpier Old Men']
# Create a Pandas Series from the list, then:
# o Print the first element
# o Print the first two elements
# o Print the last two elements
# Create a new series from the list with defined indexes: [‘a’, ’b’, ’c’].
# Print the element at index position ‘b’.

import pandas as pd

data = ['Toy Story', 'Jumanji', 'Grumpier Old Men']

# create series of a list
s = pd.Series(data)
print('\nfirst element:')
print(s.head(1).to_string())
print('\nfirst two elements:')
print(s.head(2).to_string())
print('\nlast two elements:')
print(s.tail(2).to_string())

indexed_s = pd.Series(data=data, index=['a', 'b', 'c'])
print('\nelement at index "b": ' + indexed_s['b'])
