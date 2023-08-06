# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 17:05:44 2022

@author: Pastor
"""

import pandas as pd
import numpy as np
import string
import datetime

# Run this file every month

IND = pd.DatetimeIndex(
    [
        "2021-10-28 00:00:00",
        "2021-10-28 00:30:00",
        "2021-10-28 01:00:00",
        "2021-10-28 01:30:00",
        "2021-10-28 02:00:00",
        "2021-10-28 02:30:00",
        "2021-10-28 03:00:00",
        "2021-10-28 03:30:00",
        "2021-10-28 04:00:00",
        "2021-10-28 04:30:00",
        "2021-10-28 05:00:00",
        "2021-10-28 05:30:00",
        "2021-10-28 06:00:00",
        "2021-10-28 06:30:00",
        "2021-10-28 06:45:00",
        "2021-10-28 07:00:00",
        "2021-10-28 07:15:00",
        "2021-10-28 08:30:00",
        "2021-10-28 08:45:00",
        "2021-10-28 09:15:00",
        "2021-10-28 09:45:00",
        "2021-10-28 10:15:00",
        "2021-10-28 10:45:00",
        "2021-10-28 11:15:00",
        "2021-10-28 11:45:00",
        "2021-10-28 12:15:00",
        "2021-10-28 12:45:00",
        "2021-10-28 13:15:00",
        "2021-10-28 13:45:00",
        "2021-10-28 14:15:00",
        "2021-10-28 14:45:00",
        "2021-10-28 15:15:00",
        "2021-10-28 15:45:00",
        "2021-10-28 16:15:00",
        "2021-10-28 16:45:00",
        "2021-10-28 17:15:00",
        "2021-10-28 17:45:00",
        "2021-10-28 18:15:00",
        "2021-10-28 18:45:00",
        "2021-10-28 19:15:00",
        "2021-10-28 19:45:00",
        "2021-10-28 20:15:00",
        "2021-10-28 20:45:00",
        "2021-10-28 21:15:00",
        "2021-10-28 21:45:00",
        "2021-10-28 22:15:00",
        "2021-10-28 22:45:00",
        "2021-10-28 23:15:00",
        "2021-10-28 23:45:00",
    ],
    dtype="datetime64[ns]",
    freq=None,
)

def HL_columns(df, HL = "high", day_night = "day"):
    
    first = df.columns.get_loc(f"{HL}_A_{day_night}")
    second = df.columns.get_loc(f"{HL}_B_{day_night}")
    steps = second - first
    if day_night == "day":
        last = df.columns.get_loc(f"{HL}_N_{day_night}") + 1
    else:
        last = df.columns.get_loc(f"{HL}_k_{day_night}") + 1
            
    return df.columns[first:last:steps]


def ranges_MP(df2, low_columns_day, high_columns_day):
    

    
    list_high_day = df2[high_columns_day].to_numpy().tolist()
    list_low_day = df2[low_columns_day].to_numpy().tolist()
    list_ranges = []
    
    for i in range(len(list_high_day)):
        ranges1 = np.array([])
        temp_df1 = pd.DataFrame()

        for j in range(len(list_high_day[i])):
            ranges1 = np.append(ranges1, np.arange(list_low_day[i][j], list_high_day[i][j] + 0.25, 0.25 ))
            
        temp_df1["uniques"], temp_df1["counts"] = np.unique(ranges1, return_counts=True)


        list_ranges.append(temp_df1)
        

        
    return list_ranges

    
def poc(temp_df1):
    
    high_current = temp_df1["uniques"].max()
    low_current = temp_df1["uniques"].min()
    
    half_back_current = (high_current + low_current)/2
    
    #tpo_va = round(temp_df1["counts"].sum()*0.7)
    #temp_df1_2 = temp_df1.sort_values("uniques", ascending=False)
    
    temp_df1 = temp_df1.sort_values("counts", ascending=False)
       
    temp_df1 = temp_df1[temp_df1.counts == temp_df1.counts.max()]
    temp_df1["diff"] = abs(temp_df1["uniques"] - half_back_current)
    poc_d = list(temp_df1.sort_values(by=["diff", "uniques"])["uniques"])[0]

    
    return poc_d


def width_poc_fun(temp_df1, poc_d):
    w_poc = temp_df1[temp_df1["uniques"] == poc_d]["counts"]
    
    return int(w_poc)
    

def VA(temp_df1, poc_d, width_poc):
    
    tpo_va = round(temp_df1["counts"].sum()*0.7)
    
    temp_df1_2 = temp_df1.sort_values("uniques", ascending=False)

    # New way of creating value areas
    above_poc = temp_df1_2[temp_df1_2["uniques"] > poc_d]
    above_poc = above_poc.sort_values("uniques", ascending = True)
    above_poc["indx"] = np.arange(len(above_poc)) // 2 + 1
       
    above_poc_group = above_poc.groupby('indx')["uniques"].max()
    #above_poc_group = above_poc_group.to_frame()
    above_counts = above_poc.groupby('indx')["counts"].sum()
    #above_poc_group["counts"] = above_poc.groupby('indx')["counts"].sum()
    #above_poc_group["tpo"] = "above"
     
    
    below_poc = temp_df1_2[temp_df1_2["uniques"]< poc_d]
    below_poc = below_poc.sort_values("uniques", ascending=False)
    below_poc["indx"] = np.arange(len(below_poc)) // 2 + 1
    
    below_poc_group = below_poc.groupby('indx')["uniques"].max()
    #below_poc_group = below_poc_group.to_frame()
    below_counts = below_poc.groupby('indx')["counts"].sum()

    #below_poc_group["counts"] = below_poc.groupby('indx')["counts"].sum()
    #below_poc_group["tpo"] = "below"
    
    poc_val = False
    poc_vah = False
    
    if len(below_poc_group) == 0:
        below_poc_group = pd.Series(poc_d, index = [1])
        below_counts = pd.Series([0])
        #below_poc_group = pd.DataFrame({"indx": [1], "uniques":[poc_d],"counts": [0], "tpo": ["below"]})
        poc_val = True
        val_d = poc_d
    
    if len(above_poc_group) == 0:
        above_poc_group = pd.Series(poc_d, index = [1])
        above_counts = pd.Series([0])

        #above_poc_group = pd.DataFrame({"indx": [1], "uniques":[poc_d],"counts": [0], "tpo": ["above"]})
        poc_vah = True
        vah_d = poc_d
    
    tpo = width_poc
   # per_val = 0
    #c_date = df2.index
    #c_date = c_date[0+1]
    #print(c_date)

    while tpo_va > tpo:
        #print(tpo)
        #per_val = per_val + 1
        #print(f"Percentage complete {per_val/len(df2)*100:.2f}%")
        #print(df2.index[n])
        len_above = len(above_poc_group)
        len_below = len(below_poc_group)
        
        above_va = above_poc_group.iloc[0]
        above_cn = above_counts.iloc[0]

        
        #above_cn = above_poc_group.iloc[0]["counts"]
        #above_va = above_poc_group.iloc[0]["uniques"]
        
        below_va = below_poc_group.iloc[0]
        below_cn = below_counts.iloc[0]

        
       # below_cn = below_poc_group.iloc[0]["counts"]
       # below_va = below_poc_group.iloc[0]["uniques"]
        
        if (above_cn >= below_cn) | (len_below <= 1):
            tpo = tpo + above_cn
            
            if len_above > 1:
                above_poc_group = above_poc_group.iloc[1:]
                above_counts = above_counts.iloc[1:]

                
        if (below_cn > above_cn) | (len_above <= 1):
            tpo = tpo + below_cn
            
            if len_below > 1:
                below_poc_group = below_poc_group.iloc[1:]
                below_counts = below_counts.iloc[1:]

            
    if poc_vah == False:
        vah_d = above_va
    if poc_val == False:
        val_d = below_va
        
    return (vah_d, val_d)

## left here succesful maping of the POC
def MP_features(df2, low_columns, high_columns, day_night):
    
    list_ranges_val = ranges_MP(df2, low_columns, high_columns)
    
    map_list_poc = list(map(poc,list_ranges_val))
    
    map_width_poc = list(map(width_poc_fun, list_ranges_val, map_list_poc))   
    
    value_areas = list(map(VA, list_ranges_val, map_list_poc, map_width_poc))
    
    vah, val = list(zip(*value_areas))
    
    df_MP = pd.DataFrame({f"widthpoc_{day_night}": map_width_poc,f"POC_{day_night}": map_list_poc, f"VAH_{day_night}": vah, f"VAL_{day_night}": val})
    
    #df3 = df2.append(df_MP)#, ignore_index = True)
    # percentile VA
    list_high_day = df2[high_columns].to_numpy().tolist()
    list_low_day = df2[low_columns].to_numpy().tolist()
    vah_night = []
    val_night = []
    
    for i in range(len(list_high_day)):
        ranges1 = np.array([])

        for j in range(len(list_high_day[i])):
            ranges1 = np.append(ranges1, np.arange(list_low_day[i][j], list_high_day[i][j] + 0.25, 0.25 ))


        ranges1.sort()
        val_n, _, vah_n = np.percentile(ranges1, [15, 50, 85])
        vah_night.append(round(vah_n, 2))
        val_night.append(round(val_n, 2))

    df_MP[f"VAH_{day_night}_percentile"] = vah_night
    df_MP[f"VAL_{day_night}_percentile"] = val_night

    
    return df_MP

def moving_MP(df2, df_mp, low_columns_day, high_columns_day):
    
    # df2 is high - low data
    # df_mp is data from full dataframe
    
    list_df = []

    for i in range(1, len(low_columns_day)+1):
        let = low_columns_day[i-1][4]
        print(let)
        
        df_moving = MP_features(df2, low_columns_day[:i], high_columns_day[:i], "day")
        df_moving["index"] = df2.index
        df_moving = df_moving.set_index("index")

        
        list_df.append(df_moving)

    for i in range(len(list_df)):
        let = low_columns_day[i][4]
        
        list_df[i].columns = list_df[i].columns.str.replace('_', f'_{let}_')

    for i in range(len(list_df)):
        df_mp = pd.concat([df_mp, list_df[i]], axis=1)
        
    return df_mp



def adjustments(df):
    global IND
    ohlc_dict = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "trade": "sum",
    }
    df2 = df.resample("15Min").apply(ohlc_dict).dropna()
    df2 = df2.asfreq(freq="900S")
    df2["weekday"] = df2.index.weekday
    df2[df2.columns] = df2[df2.columns].shift(-38)
    df2.dropna(inplace=True)
    as_list = df2.index.to_list()
    for i, item in enumerate(as_list):
        if item.weekday() == 6:
            as_list[i] = item - pd.DateOffset(days=2)

    df2.index = as_list
    df2.drop("weekday", axis=1, inplace=True)
    rest_sessions = df2[
        (df2.index.hour == 7) | ((df2.index.hour == 8) & (df2.index.minute == 30))
    ]
    day_sessions = df2[(df2.index.hour >= 0) & (df2.index.hour <= 6)]
    day_sessions_1 = day_sessions[day_sessions.index.time != datetime.time(6, 45)]
    day_sessions_2 = day_sessions[day_sessions.index.time == datetime.time(6, 45)]
    day_sessions_1 = day_sessions_1.resample("30Min").apply(ohlc_dict)
    #day_sessions = day_sessions_1.append(day_sessions_2)
    day_sessions = pd.concat([day_sessions_1, day_sessions_2])
    day_ohlc = day_sessions_1.resample("1440Min").apply(ohlc_dict).dropna()
    # day_sessions = day_sessions.append(rest_sessions)
    day_sessions.sort_index(inplace=True)
    night_sessions = (
        df2[(df2.index.hour >= 9) | ((df2.index.hour == 8) & (df2.index.minute >= 45))]
        .resample("30Min", origin="8:45:00")
        .apply(ohlc_dict)
        .dropna()
    )
    #night_sessions = night_sessions.append(rest_sessions)
    night_sessions = pd.concat([night_sessions, rest_sessions])
    night_sessions.sort_index(inplace=True)
    night_ohlc = night_sessions.resample("1440Min").apply(ohlc_dict).dropna()
    #df2 = day_sessions.append(night_sessions)
    df2 = pd.concat([day_sessions, night_sessions])
    df2.sort_index(inplace=True)
    df2.dropna(inplace=True)
    # df_mini = df2[str(df2.index.date[49])]
    df_mini = IND
    notn = (
        list(string.ascii_uppercase)[:15]
        + list(string.ascii_uppercase)[:2]
        + list(string.ascii_uppercase)[3:24]
        + list(string.ascii_lowercase)[:11]
    )
    for n, i, j in zip(range(len(notn)), df_mini.hour, df_mini.minute):
        if n <= 14:
            df2[f"high_{notn[n]}_day"] = df2[
                (df2.index.hour == i) & (df2.index.minute == j)
            ]["high"]
            df2[f"low_{notn[n]}_day"] = df2[
                (df2.index.hour == i) & (df2.index.minute == j)
            ]["low"]
            df2[f"open_{notn[n]}_day"] = df2[
                (df2.index.hour == i) & (df2.index.minute == j)
            ]["open"]
            # add close of the day MP
            df2[f"close_{notn[n]}_day"] = df2[
            (df2.index.hour == i) & (df2.index.minute == j)
            ]["close"]
            # add volume to market profile day
            df2[f"volume_{notn[n]}_day"] = df2[
            (df2.index.hour == i) & (df2.index.minute == j)
            ]["trade"]
        else:
            df2[f"high_{notn[n]}_night"] = df2[
                (df2.index.hour == i) & (df2.index.minute == j)
            ]["high"]
            df2[f"low_{notn[n]}_night"] = df2[
                (df2.index.hour == i) & (df2.index.minute == j)
            ]["low"]
            #add volume to market profile night
            df2[f"volume_{notn[n]}_night"] = df2[
            (df2.index.hour == i) & (df2.index.minute == j)
            ]["trade"]

    diction = {}
    for col in df2.columns[5:]:
        diction[col] = "first"

    df_main = df2.drop(["open", "high", "low", "close", "trade"], axis=1)
    df_main = df_main.resample("1440Min").apply(diction).dropna(how="all")

    df_main[["open_day", "high_day", "low_day", "close_day", "trade_day"]] = day_ohlc
    df_main[
        ["open_night", "high_night", "low_night", "close_night", "trade_night"]
    ] = night_ohlc

    df_main = df_main.drop(["high_O_day", "low_O_day", "open_O_day","close_O_day" ,"volume_O_day"], axis=1).dropna()

    # get poc
    #df_main = poc_calc(df_main)
    high_columns_day =  HL_columns(df_main, HL = "high", day_night="day")
    low_columns_day =  HL_columns(df_main, HL = "low", day_night="day")
    high_columns_night =  HL_columns(df_main, HL = "high", day_night="night")
    low_columns_night =  HL_columns(df_main, HL = "low", day_night="night")
    
    df_day = MP_features(df_main, low_columns_day, high_columns_day, "day")
    df_night = MP_features(df_main, low_columns_night, high_columns_night, "night")
    

    df_mp = pd.concat([df_day, df_night], axis=1)
    df_mp["index"] = df_main.index
    df_mp = df_mp.set_index("index")
    
    df_mp = moving_MP(df_main, df_mp, low_columns_day, high_columns_day)
    
    df_main = pd.concat([df_main, df_mp], axis=1)
    
    df_main["POC_median_day"] = (df_main["high_day"] + df_main["low_day"])/2
    df_main["POC_median_night"] = (df_main["high_night"] + df_main["low_night"])/2

    df_main["IBH_day"], df_main["IBL_day"] = np.maximum(
        df_main["high_A_day"], df_main["high_B_day"]
    ), np.minimum(df_main["low_A_day"], df_main["low_B_day"])
    df_main["IBH_night"], df_main["IBL_night"] = np.maximum(
        df_main["high_A_night"], df_main["high_B_night"]
    ), np.minimum(df_main["low_A_night"], df_main["low_B_night"])

    return df_main


def in_range_day(df, col):
    return np.where(
        (df[col].shift(1) <= df["high_day"]) & (df[col].shift(1) >= df["low_day"]), 1, 0
    )


def Range(df):
    return np.where(
        (df["open_day"] < df["high_day"].shift(1))
        & (df["open_day"] > df["low_day"].shift(1)),
        "Within",
        np.where(df["open_day"] >= df["high_day"].shift(1), "Above", "Below"),
    ).astype(object)

if __name__ == "__main__":
    df = pd.read_csv(
        "D:/MarketProfileData/data/NQ_continuous_UNadjusted_5min.txt",
        names=["time", "open", "high", "low", "close", "trade"],
    )
    print("Processing the bulk data, please wait...")
    df["time"] = pd.to_datetime(df["time"])
    df.set_index("time", inplace=True)

    df = adjustments(df)
    df.to_csv("D:/MarketProfileData/out/NQ_market_profile_master_vol_close.csv")
