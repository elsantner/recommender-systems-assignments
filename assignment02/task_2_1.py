import pandas as pd

data = ['Toy Story', 'Jumanji', 'Grumpier Old Men']

# create series
s = pd.Series(data)
print('first element:')
print(s.head(1).to_string())
print('\nfirst two elements:')
print(s.head(2).to_string())
print('\nlast two elements:')
print(s.tail(2).to_string())

indexed_s = pd.Series(data=data, index=['a', 'b', 'c'])
print('\nelement at index "b": ' + indexed_s['b'])
