#!/usr/bin/env python
# coding: utf-8
import os
import datetime

from simulator.shared import read_from_files
from simulator.transformer import *

START_DATE = "2020-04-01"
END_DATE = "2020-04-30"

DIR_INPUT = "./simulated-data/pkl/"
DIR_OUTPUT = "./simulated-data/training/"

# read the raw transaction data
transactions_df = read_from_files(DIR_INPUT, START_DATE, END_DATE)

# Add two features to the transactions:
# The first one will characterize whether a transaction occurs during a weekday or during the weekend.
# The second will characterize whether a transaction occurs during the day or the night.
transactions_df['TX_DURING_WEEKEND'] = transactions_df.TX_DATETIME.apply(
    is_weekend)
transactions_df['TX_DURING_NIGHT'] = transactions_df.TX_DATETIME.apply(
    is_night)

print("Added day-of-week/time-of-day flags.")

# Customer ID transformations

# We will take inspiration from the RFM (Recency, Frequency, Monetary value)
# framework proposed in {cite}VANVLASSELAER201538, and compute two of these features over three time windows.

transactions_df = transactions_df.groupby('CUSTOMER_ID').apply(
    lambda x: get_customer_spending_behaviour_features(x, windows_size_in_days=[1, 7, 30]))
transactions_df = transactions_df.sort_values(
    'TX_DATETIME').reset_index(drop=True)

print("Added customer spending data.")

# Terminal ID transformations

# The main goal will be to extract a risk score, that assesses the exposure of a given terminal ID to fraudulent transactions.
# The risk score will be defined as the average number of fraudulent transactions that occurred on a terminal ID over a time window.

transactions_df = transactions_df.groupby('TERMINAL_ID').apply(lambda x: get_count_risk_rolling_window(
    x, delay_period=7, windows_size_in_days=[1, 7, 30], feature="TERMINAL_ID"))
transactions_df = transactions_df.sort_values(
    'TX_DATETIME').reset_index(drop=True)

print("Added terminal risk assesment.")
print("Saving transformed transactions ...")

if not os.path.exists(DIR_OUTPUT):
    os.makedirs(DIR_OUTPUT)

start_date = datetime.datetime.strptime(START_DATE, "%Y-%m-%d")

for day in range(transactions_df.TX_TIME_DAYS.max()+1):
    
    transactions_day = transactions_df[transactions_df.TX_TIME_DAYS==day].sort_values('TX_TIME_SECONDS')
    
    date = start_date + datetime.timedelta(days=day)
    filename_output = date.strftime("%Y-%m-%d")
    
    # Protocol=4 required for Google Colab
    transactions_day.to_pickle(DIR_OUTPUT+filename_output+'.pkl', protocol=4)
    transactions_day.to_csv(DIR_OUTPUT+filename_output+'.csv')
    transactions_day.to_parquet(DIR_OUTPUT+filename_output+'.parquet')

print("done.")