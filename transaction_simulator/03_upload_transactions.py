#!/usr/bin/env python
# coding: utf-8
import os
import sys
import json
import time
import argparse
import requests
import datetime

from simulator.shared import read_from_files

KAFKA_HEADERS = {'content-type': 'application/vnd.kafka.json.v2+json'}


def upload_transactions(args):
    KAFKA_ENDPOINT = f"{args.bridge}/topics/{args.topic}"

    # read the raw transaction data
    transactions_df = read_from_files(args.dir, args.start, args.end)

    # remove the TX_FRAUD,TX_FRAUD_SCENARIO columns in order to simulate a 'new' transaction
    transactions_df = transactions_df.drop(['TX_FRAUD', 'TX_FRAUD_SCENARIO'], axis=1)

    NUM_TX = len(transactions_df)

    batch = []

    for index, row in transactions_df.iterrows():
        batch.append(row)

        if len(batch) % args.batch_size == 0:
            payload = {"records": []}

            for r in batch:
                record = {'value': r.to_json()}
                payload['records'].append(record)

            # post the payload with backoff/retry in case the bridge gets overloaded ...
            try:
                success = False
                retry = 0

                while not success:
                    r = requests.post(
                        KAFKA_ENDPOINT, headers=KAFKA_HEADERS, json=payload)
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
            print(f" --> uploaded {index+1}/{NUM_TX}")


def setup():

    parser = argparse.ArgumentParser()

    # kafka bridge endpoint
    parser.add_argument(
        '--bridge',
        required=True
    )

    # start and end date
    parser.add_argument(
        '--start',
        default='2020-04-01'
    )
    parser.add_argument(
        '--end',
        default='2020-04-02'
    )

    # environment
    parser.add_argument(
        '--topic',
        default='tx-inbox'
    )
    parser.add_argument(
        '--dir',
        default='./data/simulated/pkl/'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100
    )

    return parser.parse_args()


if __name__ == '__main__':
    # parse the command line parameters first
    args = setup()

    print('')
    print(f" --> Replaying transactions from {args.start} to {args.end}")

    upload_transactions(args)

    print(" --> DONE.")
