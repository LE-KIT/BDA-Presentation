import numpy as np
import pandas as pd
import os
import re
import sys
from datetime import timedelta
from datetime import datetime
from fbprophet import Prophet

def extract_country_codes(df):
    cols = df.columns
    country_codes = []
    for col in cols:
        separation_index = col.find("_")
        if separation_index != -1:
            country_codes.append(col[:separation_index])
        country_codes = list(dict.fromkeys(country_codes))    
    return country_codes


def get_net_export(df, country_codes, direction_codes=["IM", "EX"]):
    for code in country_codes:
        for direction_code in direction_codes:
            column_key = code + "_" + direction_code
            if code in df.columns:
                df[code] = df[code] + df[column_key]

            else:
                df[code] = df[column_key]
            df = df.drop(column_key, axis=1)
    return df

def rename_columns_for_prophet(df):
    renaming_dict = {}
    for col in df.columns:
        if df[col].dtype == "datetime64[ns]":
            renaming_dict[col]="ds"
        else:
            renaming_dict[col]="y"
    return df.rename(index=str, columns=renaming_dict).copy()