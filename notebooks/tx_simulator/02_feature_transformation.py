#!/usr/bin/env python
# coding: utf-8
import os
import datetime
import pandas as pd

from shared import read_from_pkl
from simulator.transformer import feature_transformation

START_DATE = "2020-04-01"
END_DATE = "2020-04-30"

DIR_INPUT = "./data/simulated/pkl/"
DIR_OUTPUT = "./data/simulated/training/"


# read the raw transaction data
transactions_df = read_from_pkl(DIR_INPUT, START_DATE, END_DATE)

# transform transactions
print("Calculating customer and terminal stats ...")
transactions_df = feature_transformation(transactions_df)

print("Saving transformed transactions ...")

if not os.path.exists(DIR_OUTPUT):
    os.makedirs(DIR_OUTPUT)

start_date = datetime.datetime.strptime(START_DATE, "%Y-%m-%d")

for day in range(transactions_df.TX_TIME_DAYS.max()+1):

    transactions_day = transactions_df[transactions_df.TX_TIME_DAYS == day].sort_values(
        'TX_TIME_SECONDS')

    date = start_date + datetime.timedelta(days=day)
    filename_output = date.strftime("%Y-%m-%d")

    # convert the datetime to unix timestamp
    transactions_day['TX_DATETIME'] = pd.to_numeric(
        transactions_df['TX_DATETIME'])
    transactions_day['TX_DATETIME'] = transactions_day['TX_DATETIME'] / 1000000000

    # write csv
    transactions_day.to_csv(DIR_OUTPUT+filename_output+'.csv', index=False)

print("done.")
