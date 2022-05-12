#!/usr/bin/env python
# coding: utf-8
import argparse

from shared import upload_transactions


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

    upload_transactions(args.bridge, args.topic, args.start,
                        args.end, args.dir, args.batch_size)

    print(" --> DONE.")
