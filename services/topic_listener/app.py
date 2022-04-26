import os

from kafka import KafkaConsumer
from json import loads

# e.g. 'transactions-kafka-bootstrap.fraud-detection.svc.cluster.local:9092'
KAFKA_SVC = os.getenv('kafka_service')
KAFKA_SVC_PORT = os.getenv('kafka_service_port')
KAFKA_TOPIC = os.getenv('kafka_topic')  # e.g. 'tx-inbox'

KAFKA_SERVER = f"{KAFKA_SVC}:{KAFKA_SVC_PORT}"

consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=[KAFKA_SERVER],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='topic-listener',
    value_deserializer=lambda x: loads(x.decode('utf-8')))

print('started the consumer ...')

for msg in consumer:
    m = msg.value
    print(f"msg: {m}")
