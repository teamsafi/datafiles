# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 11:30:18 2022

@author: Pastor
"""

# Market profile functions

def MP_Timeframes(df, day_low, day_high, featureMP, cumulative):
    import pandas as pd
    import numpy as np
    '''
    function that evaluates if we touch MP features after or at an specific timefra
    

    Parameters
    ----------
    df : Market profile dataframe with high and lows of each timeframe
    day_low : lows of the day: low_A_day; low_B_day....low_N_day
    day_high : highs of the day: high_A_day; high_B_day.
    featureMP : list of market profile features .
    cumulative : cummulative probabilities or individual probabilities.

    Returns
    -------
    timeframes_MP : dataframe with 1 or 0 if we touch the MP features of the previous day.

    '''
    if cumulative == True:
        type_feat = "after"
    else:
        type_feat = "each"
    
    timeframes_MP = pd.DataFrame()
    timeframes_MP["Date"] = df["Date"]
    
    for i in featureMP:
        for j in day_low:
            j=j[4]
            if cumulative == False:
                timeframes_MP[f'{i}_{j}'] = np.where(
                    (df[i].shift(1) <= df[f'high_{j}_day']) & 
                    (df[i].shift(1)>= df[f"low_{j}_day"]),1,0
                    )
            else:
                timeframes_MP[f'{i}_after_{j}'] = np.where(
                    (df[i].shift(1) <= df[f'high_after_{j}_day']) & 
                    (df[i].shift(1)>= df[f'low_after_{j}_day']),1,0
                    )
                

                
    return timeframes_MP


def range_open(Open, data):
    '''
    function that evaluates the range of open

    Parameters
    ----------
    Open : Open of the day-float number.
    data : dataframe that stores the high and low of the day.

    Returns
    -------
    data : subset dataframe with the range of open.

    '''
    
    if Open < data.iloc[-1]["high_day"] and Open > data.iloc[-1]["low_day"]:
        data = data[data['range'] == "Within"]
        print("Within")

    elif Open > data.iloc[-1]["high_day"]:
        data = data[data['range'] == "Above"]
        print("Above")

    elif Open < data.iloc[-1]["low_day"]:
        data = data[data['range'] == "Below"]
        print("Below")

    return data

# poc location


def poc_night(Open, data, ONPOC):
    
    # POC night location
    if Open < ONPOC:
        data = data[data["poc_night_loc"] == "Up"]
        print("Up")

    elif Open > ONPOC:
        data = data[data["poc_night_loc"] == "Down"]
        print("Down")

    return data

# is A higher than the high of B


def A_higher_B(High_A, High_B, data):
    if High_A > High_B:
        data = data[data["A_higher_B"] == 1]
        print("A is higher B")

    elif High_A < High_B:
        data = data[data["A_higher_B"] == 0]
        print("A is not higher than B")

    return data

# is B lower than the low of A


def A_lower_B(Low_A, Low_B, data):

    if Low_A < Low_B:
        data = data[data["A_lower_B"] == 1]
        print("A is lower than B")

    elif Low_A > Low_B:
        data = data[data["A_lower_B"] == 0]
        print("A is not lower than B")

    return data

# overnight width of the POC


def width_poc_night(width_poc_night, data, lci, uci):
    
    # previous night POC
    
    if width_poc_night > lci & width_poc_night < uci:
        
        data.loc[(data["width_poc_pnight"] >= lci) & (data["width_poc_pnight"] <= uci)]   
        print("width POC Normal range: ", width_poc_night)
   
    elif width_poc_night > uci:
        
        data = data[data["width_poc_pnight"] > uci]
        print("width POC above the Upper limit: ", width_poc_night)
        
    elif width_poc_night < lci:
        
        data = data[data["width_poc_pnight"] < lci]
        print("width POC Below the lower limit: ",width_poc_night)
        
    return data

def MP_filter(key_features, df_last_day, high, low, previous_Fixed, df_hist):
    
    '''   
    function that filters the data if we touch or not a specific timeframe
    
    Parameters
    ----------
    key_features : list of MP features ie. clos_day..poc_day.
    df_last_day : last day values of the market profile (series).
    high : current high of the day (float).
    low : current low of the day (float).
    previous_Fixed : dictionary that link actual values with binary touch MP feauture.
    df_hist : Historical data.

    Returns
    -------
    Dataframe that filters by MP features.

    '''
    
    for prev in key_features:
        if df_last_day[prev] > low and df_last_day[prev] < high:
            #print(prev)
            val = previous_Fixed[prev]
            df_hist = df_hist[df_hist[val] == 1]
            vals = list(previous_Fixed.values())
            keys = list(previous_Fixed.keys())
            
        else:
            vals = list(previous_Fixed.values())
            keys = list(previous_Fixed.keys())
            
    return df_hist

def MP_match_filters(columns_test, letter):
    '''
    Test if we touch market profile features with each timeframe or cummulative timeframes

    Parameters
    ----------
    columns_test : variables to filter the data ie: POC_median_night_after_E.
    letter : Timeframe to test: A-B-C-D...N.

    Returns
    -------
    dictionary that match MP feautres with columns under test on the timeframe .

    '''
    unvisited = map_MP_binary()
    col_list = [col for col in columns_test if col.endswith(letter)]
    return dict(zip(unvisited, col_list))

def map_MP_binary():
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
    return unvisited

    
