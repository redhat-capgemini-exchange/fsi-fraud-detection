#!/usr/bin/env python
# coding: utf-8
import os
import datetime

from simulator.generate import generate_dataset, add_frauds

N_CUSTOMERS = 5000
N_TERMINALS = 10000
N_DAYS = 183

START_DATE = "2020-04-01"
END_DATE = "2020-05-30"

DIR_OUTPUT = "./simulated-data/"
TX_DIR = "raw/"


# create the transactions
(customer_profiles_table, terminal_profiles_table, transactions_df) = generate_dataset(
    n_customers=N_CUSTOMERS, n_terminals=N_TERMINALS, nb_days=N_DAYS, start_date=START_DATE, r=5)

# add fraud scenarios to the tx data
transactions_df = add_frauds(
    customer_profiles_table, terminal_profiles_table, transactions_df)

# save simulated tx data
if not os.path.exists(DIR_OUTPUT):
    os.makedirs(DIR_OUTPUT)
    os.makedirs(DIR_OUTPUT+TX_DIR)

start_date = datetime.datetime.strptime(START_DATE, "%Y-%m-%d")

for day in range(transactions_df.TX_TIME_DAYS.max()+1):

    transactions_day = transactions_df[transactions_df.TX_TIME_DAYS == day].sort_values(
        'TX_TIME_SECONDS')

    date = start_date + datetime.timedelta(days=day)
    filename_output = TX_DIR + date.strftime("%Y-%m-%d")+'.pkl'
    transactions_day.to_pickle(DIR_OUTPUT+filename_output, protocol=4)

# also save the customer and terminal data
terminal_profiles_table.to_pickle(
    DIR_OUTPUT+'terminal_profiles_table.pkl', protocol=4)
customer_profiles_table.to_pickle(
    DIR_OUTPUT+'customer_profiles_table.pkl', protocol=4)
