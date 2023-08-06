import pandas as pd
from Data_configuration_vol_tf import adjustments
import datetime
import requests
import numpy as np
import json
from Data_configuration_vol_tf import in_range_day, Range, HL_columns
#from Moving_POC import poc_va_move

########### Get new NASDAQ OHLCV data################
def get_data(period=10, bar="1min", start_date = "2022-06-03", end_date = "2022-06-04"):
  '''
  live data from IBKR
  '''

  dat = pd.DataFrame(json.loads(requests.get(f"http://173.255.229.66:8000/data/nq?bar={bar}&start={start_date}&end={end_date}&limit={period}", timeout=5).json()))
  dat['t'] = pd.to_datetime(dat['t'])
  dat = dat[['t', 'o', 'h', 'l', 'c', 'v']]
  dat.columns = ['time', 'open', 'high', 'low', 'close', 'trade']
  dat.set_index('time', inplace=True)
  dat.index = dat.index + pd.to_timedelta(1, unit='h') # get california time
  return dat

def get_latest(last):
  shape = 1380
  master = pd.DataFrame()
  rang = pd.date_range(start=last.date(), end=(datetime.datetime.now() + datetime.timedelta(1)))
  for i in range(len(rang) - 1):
    #if shape==1380:
    last = rang[i]
    next = rang[i+1]
    print(f"{last}-{next}")
    data = pd.DataFrame(json.loads(requests.get(f"http://173.255.229.66:8000/data/nq?bar=5min&start={last.strftime('%Y-%m-%d')}&end={next.strftime('%Y-%m-%d')}&limit=1380").json()))
    if data.shape[0]==0:
      continue
    data.columns = ['time', 'open', 'high', 'low', 'close', 'trade']
    shape = data.shape[0]
    print(shape)
    data = data.iloc[::-1]
    data['time'] = pd.to_datetime(data['time'])
    data.set_index('time', inplace=True)
    data.index = data.index + pd.to_timedelta(1, unit='h') # from chicago time to california
    #print(data)
    data = data.loc[last:]
    #print(data)
    last = next
    master = pd.concat([master, data])
    #else:
    #  break

  return master


now = datetime.datetime.now()
next_day = now + pd.to_timedelta(1, unit="d")
date_time = now.strftime("%m/%d/%Y")

month = date_time[0:2]
day_c = date_time[3:5]
year_c = date_time[6:10]


source_data = "IBKR"


#####################################################

dest = pd.read_csv("NQ_market_profile_master_vol_close.csv", index_col="Unnamed: 0")
previous_day = dest.index[-2]
dest.index = pd.to_datetime(dest.index)

# get the last fith day so we can overlap days
last_five_date_available = dest.index[-5]


if source_data == "IBKR":
    df = get_latest(pd.to_datetime(dest.index[-2]))


    #df = get_data(period=1380, bar="5min",
     #            start_date=f'{previous_day}',
      #           end_date=f'{next_day.year}-{next_day.month}-{next_day.day}') # get data from the previous day to now

elif source_data == "barchart":

    #csv_path = "D:/MarketProfileData/data/nqm22_intraday-5min_historical-data-05-13-2022.csv"

    # uncomment this box after you run get_barchart to get data from barchart if the api is not running
    csv_path = f"D:/MarketProfileData/data/nqu22_intraday-5min_historical-data-{month}-{day_c}-{year_c}.csv"
    df = pd.read_csv(csv_path)
    df = df.iloc[:-1, :-1]
    df = df[['Time','Open', 'High', 'Low', 'Last', 'Volume']]
    df.columns = ['time', 'open', 'high', 'low', 'close', 'trade']
    df['time'] = pd.to_datetime(df['time'])
    df.set_index('time', inplace=True)
    df.sort_index(inplace=True)
    df.index = df.index + pd.to_timedelta(1, unit='h')

    #df = df.append(df2)
    #df.drop_duplicates(inplace=True)
    #df = df[~df.index.duplicated(keep="last")]
   # df.sort_index(inplace=True)


df.sort_index(inplace=True)

#df = df.loc[last_five_date_available:]

day_highs = HL_columns(dest, HL="high", day_night="day")
day_lows = HL_columns(dest, HL="low", day_night="day")




if dest.index[-1] >= df.index[0]:
    print("Processing the data, please wait...")
    df = adjustments(df)

    print(df)
    #dest = dest.append(df)
    dest = pd.concat([dest, df])
    dest.drop_duplicates(inplace=True)
    dest = dest[~dest.index.duplicated(keep="last")]
    dest.sort_index(inplace=True)
    dest["range"] = Range(dest)
    dest["pClose_touched_day"] = in_range_day(dest, "close_day")
    dest["pHOD_day"] = in_range_day(dest, "high_day")
    dest["pIBH_day"] = in_range_day(dest, "IBH_day")
    dest["pIBL_day"] = in_range_day(dest, "IBL_day")
    dest["pLOD_day"] = in_range_day(dest, "low_day")
    dest["pOpen_touched_day"] = in_range_day(dest, "open_day")
    dest["pVAH_touched_day"] = in_range_day(dest, "VAH_day")
    dest["pVAL_touched_day"] = in_range_day(dest, "VAL_day")

    dest["pVAH_touched_day_percentile"] = in_range_day(dest, "VAH_day_percentile")
    dest["pVAL_touched_day_percentile"] = in_range_day(dest, "VAL_day_percentile")

    dest["pPOC_touched_day"] = in_range_day(dest, "POC_day")
    dest["pPOC_median_day"] = in_range_day(dest, "POC_median_day")
    dest["pClose_touched_night"] = in_range_day(dest, "close_night")
    dest["pHOD_night"] = in_range_day(dest, "high_night")
    dest["pIBH_night"] = in_range_day(dest, "IBH_night")
    dest["pIBL_night"] = in_range_day(dest, "IBL_night")
    dest["pLOD_night"] = in_range_day(dest, "low_night")
    dest["pOpen_touched_night"] = in_range_day(dest, "open_night")
    dest["pVAH_touched_night"] = in_range_day(dest, "VAH_night")
    dest["pVAL_touched_night"] = in_range_day(dest, "VAL_night")

    dest["pVAH_touched_night_percentile"] = in_range_day(dest, "VAH_night_percentile")
    dest["pVAL_touched_night_percentile"] = in_range_day(dest, "VAL_night_percentile")

    dest["pPOC_touched_night"] = in_range_day(dest, "POC_night")
    dest["pPOC_median_night"] = in_range_day(dest, "POC_median_night")
    dest["A_higher_B"] = np.where(dest["high_A_day"] > dest["high_B_day"], 1, 0)
    dest["A_lower_B"] = np.where(dest["high_A_day"] < dest["high_B_day"], 1, 0)

    dest['A_higher_B'] = np.where(dest['high_A_day']>dest['high_B_day'], 1, 0)
    dest['A_lower_B'] = np.where(dest['low_A_day']<dest['low_B_day'], 1, 0)
    #dest['A_close_higher_B'] = np.where(dest['close_A_day'] < dest['close_B_day'])
    dest['Lowest_day'] = dest[day_lows].idxmin(axis="columns").str[4]
    dest['Highest_day'] = dest[day_highs].idxmax(axis="columns").str[5]

    dest['dist_poc_night_open'] = (dest['POC_night'].shift(1)-dest['open_day'])/dest['open_day']
    dest['dist_poc_open'] =  (dest['POC_day'].shift(1)-dest['open_day'])/dest['open_day']
    dest['open_close_dist'] = (dest['close_day']-dest['open_day'])/dest['open_day']
    dest['open_high_dist'] = (dest['high_day']-dest['open_day'])/dest['open_day']
    dest['open_low_dist'] = (dest['low_day']-dest['open_day'])/dest['open_day']

    for i in range(1, len(day_lows)):
        dest['L'+day_lows[i][1:5]] = (dest[day_lows[i-1]]-dest[day_lows[i]])/dest[day_lows[i-1]]
        dest['L'+day_lows[i][1:5]+'_binary'] = np.where(dest[day_lows[i-1]]>dest[day_lows[i]], 1, 0)

    for i in range(1, len(day_highs)):
        dest['H'+day_highs[i][1:6]] = (dest[day_highs[i-1]]-dest[day_highs[i]])/dest[day_highs[i-1]]
        dest['H'+day_highs[i][1:6]+'_binary'] = np.where(dest[day_highs[i-1]]<dest[day_highs[i]], 1, 0)

    dest['poc_loc'] = np.where(dest['POC_day'].shift(1)>=dest['open_day'], 'Up', 'Down')
    dest['poc_night_loc'] = np.where(dest['POC_night'].shift(1)>=dest['open_day'], 'Up', 'Down')

    dest['IBH_BK'] = np.where(dest['IBH_day']<dest['high_day'], 1, 0)
    dest['IBL_BK'] = np.where(dest['IBL_day']>dest['low_day'], 1, 0)

    #dest["Normal_Day"] = np.where((dest["IBH_BK"] == 0) & (dest["IBL_BK"] == 0))

    dest.to_csv("NQ_market_profile_master_vol_close.csv")


else:
    print(f"The data must have ticks from or on day {dest.index[-1]}")
