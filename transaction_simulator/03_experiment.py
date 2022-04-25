#!/usr/bin/env python
# coding: utf-8
import os
import datetime

from simulator.shared import read_from_files

START_DATE = "2020-04-01"
#END_DATE = "2020-05-30"
END_DATE = "2020-04-30"

DIR_INPUT = "./simulated-data/tx/"
DIR_OUTPUT = "./simulated-data/tx/"

# read the raw transaction data
transactions_df = read_from_files(DIR_INPUT, START_DATE, END_DATE)

print(transactions_df.head(10))