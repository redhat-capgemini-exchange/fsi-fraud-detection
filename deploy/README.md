## Deploy the Infrastructure

#### Kafka

Once the Kafka Operator is installed, create the various instances:

```shell
oc apply -f deploy/kafka.yaml
oc apply -f deploy/kafka-topics.yaml
oc apply -f deploy/kafka-bridge.yaml
oc apply -f deploy/kafka-bridge-route.yaml
```
