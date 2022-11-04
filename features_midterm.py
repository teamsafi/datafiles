# -*- coding: utf-8 -*-
"""
Created on Sat Mar  5 15:51:09 2022

@author: Pastor
"""

# Features to Midterm strategy

import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
from datetime import datetime
import string
import statistics
import warnings
warnings.filterwarnings("ignore")
from Data_configuration_vol_tf import HL_columns

# run the first two script
#print("Barchar data in process....")
#import get_barchart
print("incrementa file in progress")
import incremental_ret

print("Features mideterm in progress")
from MP_analysis import MP_Timeframes, range_open, poc_night, A_higher_B, A_lower_B, width_poc_night, MP_filter, MP_match_filters, map_MP_binary

path = "D:/MarketProfileData/out/NQ_market_profile_master_vol_close.csv"

raw_data = pd.read_csv(path)
df = raw_data.rename(columns={'Unnamed: 0': 'Date'})

# add features to historical data
df["width_poc_pday"] = df["widthpoc_day"].shift(1)
df["width_poc_pnight"] = df["widthpoc_night"].shift(1)
df["vol_A_ret"] = df["volume_A_day"].pct_change()
df["vol_B_ret"] = df["volume_B_day"].pct_change()

# get lows and highs of the day

day_lows = HL_columns(df, HL="low", day_night = "day")
day_highs = HL_columns(df, HL="high", day_night = "day")
day_close = HL_columns(df, HL="close", day_night = "day")


# add low and highs after each timeframe
for i in range(0,len(day_lows)):
    tf = day_lows[i][4]
    df[f"low_after_{tf}_day"] = df[day_lows[i:]].min(axis=1)
    df[f'high_after_{tf}_day'] = df[day_highs[i:]].max(axis=1)
    df[f'half_back_{tf}_day'] = (df[f'high_{tf}_day'] + df[f'low_{tf}_day'])/2

df["low_after_N_day"] = df["low_N_day"]
df['high_after_N_day'] = df["high_N_day"]

### gap days
# fill the gap
df["fill_gap_up"] = np.where((df["high_day"].shift(1) > df["low_A_day"]) & (df["range"] == "Above"), 1,0)
df["fill_gap_down"] = np.where((df["low_day"].shift(1) < df["high_A_day"]) & (df["range"] == "Below"), 1,0)


# dictionary that links value with binary in all timeframes
previous_Fixed = {
    "close_day": "pClose_touched_day",
    "high_day": "pHOD_day",
    "IBH_day": "pIBH_day",
    "VAL_day": "pVAL_touched_day",
    "open_day": "pOpen_touched_day",
    "POC_day": "pPOC_touched_day",
    "low_day": "pLOD_day",
    "IBL_day": "pIBL_day",
    "VAH_day": "pVAH_touched_day",
    "POC_median_day": "pPOC_median_day",
    "high_night": "pHOD_night",
    "IBH_night": "pIBH_night",
    "VAL_night": "pVAL_touched_night",
    "VAH_night": "pVAH_touched_night",
    "open_night": "pOpen_touched_night",
    "POC_night": "pPOC_touched_night",
    "low_night": "pLOD_night",
    "IBL_night": "pIBL_night",
    "POC_median_night": "pPOC_median_night",
}

unvisited = list(previous_Fixed.keys())  # keys of the dictionary

# probability of touching after the timeframe
mp_after_c = MP_Timeframes(df, day_lows, day_highs, unvisited, True)
# prob to touch on each timeframe
timeframes_profile = MP_Timeframes(df, day_lows, day_highs, unvisited, False)
# data with all the new features
full_data = pd.merge(df, mp_after_c, how='outer', on = "Date")
full_data = pd.merge(full_data, timeframes_profile, how='outer', on = "Date")

# range of the day session
full_data["range_day"] = full_data["high_day"] - full_data["low_day"]
full_data["range_day_log"] = np.log(full_data["range_day"]/full_data["open_day"])

# we use the last 1190 days to match the procedures by shane
ave_range = statistics.mean(full_data["range_day"])
std_range = statistics.stdev(full_data["range_day"])
above_mean_range = ave_range + std_range

# where do we open compared to the previous day IB
full_data["IB_open_range"] = np.where(
    (full_data["open_day"] < full_data["IBH_day"].shift(1))
    & (full_data["open_day"] > full_data["IBL_day"].shift(1)),
    "WithinIB",
    np.where(full_data["open_day"] >= full_data["IBH_day"].shift(1), "AboveIB", "BelowIB"),

)

# half way back IB
full_data["half_back_IB"] = (full_data["IBH_day"] + full_data["IBL_day"])/2
# both IB are broken
full_data["IB_BK"] = np.where((full_data["IBH_BK"] == 1) & (full_data["IBL_BK"]==1),1,0)
full_data["high_25"] = full_data["high_day"] - full_data["range_day"] * 0.25
full_data["low_25"] = full_data["low_day"] + (full_data["range_day"] * 0.25)

# types of days
# normal day: both IBH and IBL are not broken
full_data["normal_day"] = np.where((full_data["IBH_BK"] == 0) & (full_data["IBL_BK"] == 0),1,0 )
# normal variation day: either IBH or IBL are broken at some point
full_data["normal_variation_day"] =  np.where((full_data["IBH_BK"] == 1) | (full_data["IBL_BK"] == 1),1,0 )
# trend day: range > 1sd above mean close within 25% range high or low
full_data["trend_day_up"] = np.where(
    ((full_data["IBH_BK"] == 1) & (full_data["IBL_BK"] == 0)) & (full_data["range_day"] > above_mean_range) & (full_data["close_day"] > full_data["high_25"]), 1, 0
    )

full_data["trend_day_down"] = np.where(
    ((full_data["IBL_BK"] == 1) & (full_data["IBH_BK"] == 0)) & (full_data["range_day"] > above_mean_range) & (full_data["close_day"] < full_data["low_25"]), 1, 0
    )

# Neutral day: both IBH and IBL are broken and market close within the IB
full_data["neutral_day"] = np.where((full_data["IB_BK"] == 1) &
 (full_data["close_day"] > full_data["IBL_day"]) &
 (full_data["close_day"] < full_data["IBH_day"]),1,0)
# neutral extreme high day: Both IB are broken and the close of the day is above the high of IB
full_data["neutral_extreme_high_day"] = np.where((full_data["IB_BK"] == 1) &
 (full_data["close_day"] > full_data["IBH_day"]) ,1,0)
# neutral extreme low day
full_data["neutral_extreme_low_day"] = np.where((full_data["IB_BK"] == 1) &
 (full_data["close_day"] < full_data["IBL_day"]) ,1,0)


full_data.to_csv("midterm_data.csv", index = False)

print("Prepare minute data")
import Incremental_MP_Minute_data

print("End of the script!")

