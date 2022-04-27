import os
import datetime

from kafka import KafkaConsumer, KafkaProducer
from json import loads, dumps

# KAFKA server config
KAFKA_SVC = os.getenv('kafka_service')
KAFKA_SVC_PORT = os.getenv('kafka_service_port')
KAFKA_SERVER = f"{KAFKA_SVC}:{KAFKA_SVC_PORT}"

# service config
SOURCE_TOPIC = os.getenv('source_topic')
TARGET_TOPIC = os.getenv('target_topic')

CLIENT_ID = os.getenv('client_id')
GROUP_ID = os.getenv('group_id')


def is_weekend(tx_datetime):

    # Transform date into weekday (0 is Monday, 6 is Sunday)
    weekday = tx_datetime.weekday()
    # Binary value: 0 if weekday, 1 if weekend
    is_weekend = weekday >= 5

    return int(is_weekend)


def is_night(tx_datetime):

    # Get the hour of the transaction
    tx_hour = tx_datetime.hour
    # Binary value: 1 if hour less than 6, and 0 otherwise
    is_night = tx_hour <= 6

    return int(is_night)


def transform(tx):
    # first 2 new features
    tx_dt = datetime.datetime.fromtimestamp(tx['TX_DATETIME']/1000)
    tx['TX_DURING_WEEKEND'] = is_weekend(tx_dt)
    tx['TX_DURING_NIGHT'] = is_night(tx_dt)

    # TX_FRAUD,TX_FRAUD_SCENARIO -> -1 i.e. we don't know ...
    tx['TX_FRAUD'] = -1
    tx['TX_FRAUD_SCENARIO'] = -1

    # CUSTOMER_ID_NB_TX_1DAY_WINDOW,CUSTOMER_ID_AVG_AMOUNT_1DAY_WINDOW,CUSTOMER_ID_NB_TX_7DAY_WINDOW,CUSTOMER_ID_AVG_AMOUNT_7DAY_WINDOW,CUSTOMER_ID_NB_TX_30DAY_WINDOW,CUSTOMER_ID_AVG_AMOUNT_30DAY_WINDOW,TERMINAL_ID_NB_TX_1DAY_WINDOW,TERMINAL_ID_RISK_1DAY_WINDOW,TERMINAL_ID_NB_TX_7DAY_WINDOW,TERMINAL_ID_RISK_7DAY_WINDOW,TERMINAL_ID_NB_TX_30DAY_WINDOW,TERMINAL_ID_RISK_30DAY_WINDOW
    tx['CUSTOMER_ID_NB_TX_1DAY_WINDOW'] = 0
    tx['CUSTOMER_ID_AVG_AMOUNT_1DAY_WINDOW'] = 0
    tx['CUSTOMER_ID_NB_TX_7DAY_WINDOW'] = 0
    tx['CUSTOMER_ID_AVG_AMOUNT_7DAY_WINDOW'] = 0
    tx['CUSTOMER_ID_NB_TX_30DAY_WINDOW'] = 0
    tx['CUSTOMER_ID_AVG_AMOUNT_30DAY_WINDOW'] = 0
    tx['TERMINAL_ID_NB_TX_1DAY_WINDOW'] = 0
    tx['TERMINAL_ID_RISK_1DAY_WINDOW'] = 0
    tx['TERMINAL_ID_NB_TX_7DAY_WINDOW'] = 0
    tx['TERMINAL_ID_RISK_7DAY_WINDOW'] = 0
    tx['TERMINAL_ID_NB_TX_30DAY_WINDOW'] = 0
    tx['TERMINAL_ID_RISK_30DAY_WINDOW'] = 0

    return tx


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
    tx = transform(tx)

    # send it along
    producer.send(TARGET_TOPIC, value=tx)

    # basic logging, because demo
    print(
        f" --> {tx['TRANSACTION_ID']}:[{tx['TX_DATETIME']},{tx['TERMINAL_ID']},{tx['TX_AMOUNT']}]")
