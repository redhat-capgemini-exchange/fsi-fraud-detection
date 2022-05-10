import os
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
