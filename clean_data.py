import pandas as pd

midterm = pd.read_csv('midterm_data.csv')
midterm = midterm.drop(midterm.tail(100).index)
print('Midterm data')
print(midterm.tail(1))
midterm.to_csv('midterm_data.csv', index=False)

print()

nq = pd.read_csv('NQ_market_profile_master_vol_close.csv')
nq = nq.drop(nq.tail(250).index)
print('NQ data')
print(nq.tail(1))
nq.to_csv('NQ_market_profile_master_vol_close.csv', index=False)
