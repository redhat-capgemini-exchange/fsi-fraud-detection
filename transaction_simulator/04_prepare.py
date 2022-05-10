#!/usr/bin/env python
# coding: utf-8
import os
import datetime
import pandas as pd

from simulator.transformer import *
from simulator.shared import merge_csv_files

DIR_AUDIT_INPUT = "./data/audit/"
DIR_TRAINING_INPUT = "./data/simulated/training"
DIR_OUTPUT = "./data/training/"

TIME_WINDOW = 30


# read the files
transactions_df = merge_csv_files([DIR_AUDIT_INPUT, DIR_TRAINING_INPUT])

# convert timestamp to datetime
transactions_df['TX_DATETIME'] = pd.to_datetime(
    transactions_df['TX_DATETIME'] * 1000000000)


#d = datetime.datetime.today() - datetime.timedelta(days=TIME_WINDOW)

# find the latest date in the dataframe and filter rows in the defined time window
d = transactions_df['TX_DATETIME'].max() - datetime.timedelta(days=TIME_WINDOW)
filtered_df = transactions_df.loc[transactions_df['TX_DATETIME'] > d.strftime(
    "%Y-%m-%d")]

# transform transactions, i.e. calculate the
print("Calculating customer and terminal stats ...")
filtered_df = process_transactions(filtered_df)

print("Saving transformed transactions ...")

if not os.path.exists(DIR_OUTPUT):
    os.makedirs(DIR_OUTPUT)

ts = int(datetime.datetime.timestamp(datetime.datetime.now()) * 100000)
file_name = f"training_{ts}.csv"

filtered_df.to_csv(DIR_OUTPUT+file_name, index=False)
filtered_df.to_csv(DIR_OUTPUT+"training_latest.csv", index=False)
