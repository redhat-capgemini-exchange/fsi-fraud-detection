import os
import sys
import json
import time
import requests
import datetime
import pandas as pd
import boto3

from pathlib import Path


def load_csv_from_dir(input_dir, begin_date, end_date):

    files = [os.path.join(input_dir, f) for f in os.listdir(
        input_dir) if f >= begin_date+'.csv' and f <= end_date+'.csv']

    frames = []
    for f in files:
        try:
            df = pd.read_csv(f)
            frames.append(df)
            del df
        except:
            print(f" --> skipping file '{f}'")

    df_final = pd.concat(frames)

    df_final = df_final.sort_values('TRANSACTION_ID')
    df_final.reset_index(drop=True, inplace=True)

    #  Note: -1 are missing values for real world data
    df_final = df_final.replace([-1], 0)

    return df_final


def merge_csv_files(file_collection):
    frames = []
    for f in file_collection:
        df = df = pd.read_csv(f)
        frames.append(df)
        del df

    df_final = pd.concat(frames)

    return df_final


def load_transactions(file_collection, cutoff_date=None, time_window=-1):
    tx_df = merge_csv_files(file_collection)
    
    tx_df = tx_df.sort_values('TRANSACTION_ID')
    tx_df.reset_index(drop=True, inplace=True)

    # TX_DATETIME is in UNIX time in the files. This needs conversion for more advanced calculations, e.g. rolling time-windows
    tx_df['TX_DATETIME'] = pd.to_datetime(tx_df['TX_DATETIME'] * 1000000000)

    if cutoff_date == None and time_window == -1:
        return tx_df  # return all transactions

    if cutoff_date != None and time_window == -1:
        return transactions_df.loc[transactions_df['TX_DATETIME'] > cutoff_date.strftime("%Y-%m-%d")]

    if cutoff_date == None and time_window > -1:
        # return the n last days
        d = tx_df['TX_DATETIME'].max() - datetime.timedelta(days=time_window + 1)
        return tx_df.loc[tx_df['TX_DATETIME'] > d.strftime("%Y-%m-%d")]

    # if cutoff_date != None and time_window > -1:
    # this is not supported yet!

    return td_df


def download_bucket_folder(key, bucket_name='fsi-fraud-detection', local_prefix='./data/'):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)

    objs = list(bucket.objects.filter(Prefix=key))

    for obj in objs:
        # remove the file name from the object key
        obj_path = f"{local_prefix}{os.path.dirname(obj.key)}"
        # create nested directory structure
        Path(obj_path).mkdir(parents=True, exist_ok=True)
        # save file with full path locally
        bucket.download_file(obj.key, local_prefix + obj.key)


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