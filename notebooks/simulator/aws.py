import os
import sys
import boto3

from pathlib import Path


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
