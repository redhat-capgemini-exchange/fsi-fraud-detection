import os
import datetime
import pandas as pd


def read_from_pkl(input_dir, begin_date, end_date):

    files = [os.path.join(input_dir, f) for f in os.listdir(
        input_dir) if f >= begin_date+'.pkl' and f <= end_date+'.pkl']

    frames = []
    for f in files:
        try:
            df = pd.read_pickle(f)
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


def read_from_csv(input_dir):

    files = [os.path.join(input_dir, f) for f in os.listdir(input_dir)]

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
        df = read_from_csv(f)
        frames.append(df)
        del df

    df_final = pd.concat(frames)
    df_final = df_final.sort_values('TRANSACTION_ID')
    df_final.reset_index(drop=True, inplace=True)

    return df_final


def load_transactions(file_collection, cutoff_date=None, time_window=-1):
    tx_df = merge_csv_files(file_collection)

    # TX_DATETIME is in UNIX time in the files. This needs conversion for more advanced calculations, e.g. rolling time-windows
    tx_df['TX_DATETIME'] = pd.to_datetime(tx_df['TX_DATETIME'] * 1000000000)

    if cutoff_date == None and time_window == -1:
        return td_df # return all transactions

    if cutoff_date != None and time_window == -1:
        return transactions_df.loc[transactions_df['TX_DATETIME'] > cutoff_date.strftime("%Y-%m-%d")]

    if cutoff_date == None and time_window > -1:
        # return the n last days
        d = tx_df['TX_DATETIME'].max() - datetime.timedelta(days=time_window + 1)
        return tx_df.loc[tx_df['TX_DATETIME'] > d.strftime("%Y-%m-%d")]

    # if cutoff_date != None and time_window > -1:
    # this is not supported yet!

    return td_df