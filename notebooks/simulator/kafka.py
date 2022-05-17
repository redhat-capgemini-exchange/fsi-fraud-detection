import sys
import json
import time
import requests
import pandas as pd

from simulator.shared import read_from_pkl, read_from_csv


def divts(ts):
    return int(ts / 1000000000)


def post_to_kafka_bridge(endpoint, batch):
    KAFKA_HEADERS = {'content-type': 'application/vnd.kafka.json.v2+json'}

    payload = {"records": []}
    for r in batch:
        record = {'value': r.to_json()}
        payload['records'].append(record)

    # post the payload with backoff/retry in case the bridge gets overloaded ...
    try:
        success = False  # change to False
        retry = 0

        while not success:
            r = requests.post(endpoint, headers=KAFKA_HEADERS, json=payload)
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


def upload_transactions(bridge, topic='tx-sim', start='2020-05-01', end='2020-05-01', loc='./data/simulated/csv/', batch_size=100):

    KAFKA_ENDPOINT = f"{bridge}/topics/{topic}"

    # read the raw transaction data
    transactions_df = read_from_csv(loc, start, end)

    # convert to UNIX time to avoid issues later on
    #transactions_df['TX_DATETIME'] = pd.to_numeric(transactions_df['TX_DATETIME']).apply(divts)

    NUM_TX = len(transactions_df)

    batch = []
    for index, row in transactions_df.iterrows():
        batch.append(row)

        if len(batch) % batch_size == 0:
            post_to_kafka_bridge(KAFKA_ENDPOINT, batch)

            batch = []
            print(f" --> uploaded {index+1}/{NUM_TX}")

    if len(batch) > 0:
        post_to_kafka_bridge(KAFKA_ENDPOINT, batch)
        print(f" --> uploaded remaining {len(batch)}/{NUM_TX}")


def upload_fraud(bridge, topic='tx-fraud-sim', start='2020-04-01', end='2020-04-01', loc='./data/simulated/fraud/', batch_size=100):

    KAFKA_ENDPOINT = f"{bridge}/topics/{topic}"

    # read the raw transaction data
    transactions_df = read_from_csv(loc, start, end)
    NUM_TX = len(transactions_df)

    batch = []

    for index, row in transactions_df.iterrows():
        batch.append(row)

        if len(batch) % batch_size == 0:
            post_to_kafka_bridge(KAFKA_ENDPOINT, batch)

            batch = []
            print(f" --> uploaded {index+1}/{NUM_TX}")

    if len(batch) > 0:
        post_to_kafka_bridge(KAFKA_ENDPOINT, batch)
        print(f" --> uploaded remaining {len(batch)}/{NUM_TX}")
