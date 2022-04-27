import os

from kafka import KafkaConsumer, KafkaProducer
from json import loads, dumps

# KAFKA server config
KAFKA_SVC = os.getenv('kafka_service')
KAFKA_SVC_PORT = os.getenv('kafka_service_port')
KAFKA_SERVER = f"{KAFKA_SVC}:{KAFKA_SVC_PORT}"

# service config
SOURCE_TOPIC = os.getenv('source_topic')

ARCHIVE_TOPIC = os.getenv('archive_topic')
FRAUD_TOPIC = os.getenv('fraud_topic')

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
    # no idea, why we need a dubble loads ...
    tx = loads(msg.value)

    # transform the data
    #tx = transform(tx)

    # just some forced routing ...
    if tx['TX_AMOUNT'] > 60:
        tx['TX_FRAUD'] = 1
        tx['TX_FRAUD_SCENARIO'] = 42
        producer.send(FRAUD_TOPIC, value=tx)
    else:
        producer.send(ARCHIVE_TOPIC, value=tx)

    # basic logging, because demo
    print(
        f" --> {tx['TRANSACTION_ID']}:[{tx['TX_DATETIME']},{tx['TERMINAL_ID']},{tx['TX_AMOUNT']}]")
