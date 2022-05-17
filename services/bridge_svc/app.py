import os
import datetime
import pandas as pd

from kafka import KafkaConsumer, KafkaProducer
from json import loads, dumps

import warnings
warnings.filterwarnings("ignore")

# KAFKA server config
KAFKA_SVC = os.getenv('kafka_service')
KAFKA_SVC_PORT = os.getenv('kafka_service_port')
KAFKA_SERVER = f"{KAFKA_SVC}:{KAFKA_SVC_PORT}"

# service config
SOURCE_TOPIC = os.getenv('source_topic')
TARGET_TOPIC = os.getenv('target_topic')

CLIENT_ID = os.getenv('client_id')
GROUP_ID = os.getenv('group_id')


consumer = KafkaConsumer(
    SOURCE_TOPIC,
    bootstrap_servers=[KAFKA_SERVER],
    auto_offset_reset='earliest',
    consumer_timeout_ms=-1,
    enable_auto_commit=True,
    client_id=CLIENT_ID,
    group_id=GROUP_ID,
    value_deserializer=lambda x: loads(x.decode('utf-8')))

producer = KafkaProducer(bootstrap_servers=[
                         KAFKA_SERVER], value_serializer=lambda x: dumps(x).encode('utf-8'))

print(f" --> listening on topic '{SOURCE_TOPIC}'")

for msg in consumer:
    # no idea, why we need the double loads ...
    tx = loads(msg.value)

    # convert datetime to UNIX timestamp
    if type(tx['TX_DATETIME']) == str:
        tx['TX_DATETIME'] = int(datetime.datetime.strptime(tx['TX_DATETIME'], "%Y-%m-%d %H:%M:%S").timestamp())

    # just send it to the next topic
    producer.send(TARGET_TOPIC, value=tx)

    # basic logging, because demo
    print(
        f" --> {tx['TRANSACTION_ID']}:[{tx['TX_DATETIME']},{tx['TERMINAL_ID']},{tx['TX_AMOUNT']}]")
