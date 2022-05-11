#!/usr/bin/env python
# coding: utf-8
import argparse

from shared import post_transactions


def setup():

    parser = argparse.ArgumentParser()

    # start and end date
    parser.add_argument(
        '--start',
        default='2020-04-01'
    )
    parser.add_argument(
        '--end',
        default='2020-04-01'
    )

    # environment
    parser.add_argument(
        '--endpoint',
        default='http://127.0.0.1:5000/predict'
    )
    parser.add_argument(
        '--dir',
        default='./data/audit/'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=1
    )

    return parser.parse_args()


if __name__ == '__main__':
    # parse the command line parameters first
    args = setup()

    print('')
    print(f" --> Posting transactions from {args.start} to {args.end}")

    post_transactions(args.endpoint, args.start, args.end, args.dir, args.batch_size)

    print(" --> DONE.")
