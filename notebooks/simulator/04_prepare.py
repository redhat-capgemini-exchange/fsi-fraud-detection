#!/usr/bin/env python
# coding: utf-8
import os
import pandas as pd

from simulator.transformer import *
from simulator.shared import load_transactions

DIR_AUDIT_INPUT = "./data/audit/"
DIR_TRAINING_INPUT = "./data/simulated/training"
DIR_OUTPUT = "./data/training/"

# load and filter the transactions
filtered_df = load_transactions(
    [DIR_AUDIT_INPUT, DIR_TRAINING_INPUT], time_window=30)


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
