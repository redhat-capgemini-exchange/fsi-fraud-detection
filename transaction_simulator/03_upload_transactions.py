#!/usr/bin/env python
# coding: utf-8
import os
import sys
import json
import time
import pandas as pd
import requests
import datetime

from simulator.shared import read_from_files

KAFKA_BRIDGE_ROUTE = 'https://transaction-bridge-http-fraud-detection.apps.cluster-4gcwb.4gcwb.sandbox682.opentlc.com'
KAFKA_TOPIC = 'tx-inbox'

DIR_INPUT = "./simulated-data/tx/"
#
START_DATE = "2020-04-01"
END_DATE = "2020-04-30"

KAFKA_HEADERS = {'content-type': 'application/vnd.kafka.json.v2+json'}
KAFKA_ENDPOINT = f"{KAFKA_BRIDGE_ROUTE}/topics/{KAFKA_TOPIC}"

# read the raw transaction data
transactions_df = read_from_files(DIR_INPUT, START_DATE, END_DATE)
NUM_TX = len(transactions_df)

batch = []
batch_size = 100

for index, row in transactions_df.iterrows():
    batch.append(row)

    if len(batch) % batch_size == 0:
        payload = {"records": []}

        for r in batch:
            record = {'value': r.to_json()}
            payload['records'].append(record)

        try:
            success = False
            retry = 0

            while not success:
                r = requests.post(KAFKA_ENDPOINT, headers=KAFKA_HEADERS, json=payload)
                if r.status_code == 200:
                    success = True
                else:
                    retry = retry + 1
                    if retry > 5:
                        print('aborting...')
                        sys.exit()
                    time.sleep(retry * 2)
                    print(f"backing-off/retry {retry}/5")
        except:
            print('exception/aborting...')
            sys.exit()

        batch = []
        print(f"uploaded {index+1}/{NUM_TX}")

print("done.")
