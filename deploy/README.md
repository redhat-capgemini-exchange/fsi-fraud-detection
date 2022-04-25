## Deploy the Infrastructure

#### Namespace

```shell
oc new-project fraud-detection
```

All subsequent deployment commands are preformed in the context of this project/namespace.

#### RH AMQ Streams / Kafka

Once the Kafka Operator is installed, create the various instances:

```shell
oc apply -f deploy/kafka.yaml -n fraud-detection
oc apply -f deploy/kafka-topics.yaml -n fraud-detection
oc apply -f deploy/kafka-bridge.yaml -n fraud-detection
oc apply -f deploy/kafka-bridge-route.yaml -n fraud-detection
```
