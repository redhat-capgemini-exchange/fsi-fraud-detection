import os

from kafka import KafkaConsumer
from json import loads

# KAFKA server config
KAFKA_SVC = os.getenv('kafka_service')
KAFKA_SVC_PORT = os.getenv('kafka_service_port')
KAFKA_SERVER = f"{KAFKA_SVC}:{KAFKA_SVC_PORT}"

# service config
SOURCE_TOPIC = os.getenv('source_topic')

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

print(f" --> listening on topic '{SOURCE_TOPIC}'")

for msg in consumer:
    # no idea, why we need a dubble loads ...
    tx = msg.value

    # do nothing this is a sink

    # basic logging, because demo
    print(
        f" --> {tx['TRANSACTION_ID']}:[{tx['TX_DATETIME']},{tx['TERMINAL_ID']},{tx['TX_AMOUNT']}]")
