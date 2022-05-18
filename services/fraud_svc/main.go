package main

import (
	"encoding/json"
	"fmt"

	"github.com/confluentinc/confluent-kafka-go/kafka"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"

	"github.com/txsvc/stdlib/v2/env"

	"github.com/redhat-capgemini-exchange/fsi-fraud-detection/internal"
)

var (
	kc *kafka.Consumer
	kp *kafka.Producer
)

func init() {

	clientID := env.GetString("client_id", "fraud-svc")
	groupID := env.GetString("group_id", "fsi-fraud-detection")

	kafkaService := env.GetString("kafka_service", "")
	if kafkaService == "" {
		panic(fmt.Errorf("missing env 'kafka_service'"))
	}
	kafkaServicePort := env.GetString("kafka_service_port", "9092")
	kafkaServer := fmt.Sprintf("%s:%s", kafkaService, kafkaServicePort)

	// https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
	_kc, err := kafka.NewConsumer(&kafka.ConfigMap{
		"bootstrap.servers":       kafkaServer,
		"client.id":               clientID,
		"group.id":                groupID,
		"connections.max.idle.ms": 0,
		"auto.offset.reset":       "earliest",
		"broker.address.family":   "v4",
	})
	if err != nil {
		panic(err)
	}
	kc = _kc

	_kp, err := kafka.NewProducer(&kafka.ConfigMap{
		"bootstrap.servers": kafkaServer,
	})
	if err != nil {
		panic(err)
	}
	kp = _kp

	// prometheus endpoint setup
	internal.StartPrometheusListener()
}

func main() {

	clientID := env.GetString("client_id", "fraud-svc")
	sourceTopic := env.GetString("source_topic", "tx-fraud")
	archiveTopic := env.GetString("archive_topic", "tx-archive")
	fraudTopic := env.GetString("fraud_topic", "tx-fraud")
	rulesAppEndpoint := env.GetString("rules_app_svc", "http://rules-app-svc.fsi-fraud-detection.svc.cluster.local:8080/validate")
	fraudAppEndpoint := env.GetString("fraud_app_svc", "http://fraud-app-svc.fsi-fraud-detection.svc.cluster.local:8080/predict")

	// metrics
	opsTxProcessed := promauto.NewCounter(prometheus.CounterOpts{
		Name: "fraud_processed_transactions",
		Help: "The number of processed transactions",
	})

	// create a responder for delivery notifications
	evts := make(chan kafka.Event, 1000) // FIXME not sure if such a number is needed ...
	go func() {
		fmt.Printf(" --> %s: listening for delivery events\n", clientID)
		for {
			e := <-evts

			switch ev := e.(type) {
			case *kafka.Message:
				if ev.TopicPartition.Error != nil {
					fmt.Printf(" --> delivery error: %v\n", ev.TopicPartition)
				}
			}
		}
	}()

	// subscriber
	err := kc.SubscribeTopics([]string{sourceTopic}, nil)
	if err != nil {
		panic(err)
	}

	fmt.Printf(" --> %s: listening on topic '%s'\n", clientID, sourceTopic)

	for {
		msg, err := kc.ReadMessage(-1)
		if err == nil {
			nextTopic := archiveTopic
			var resp internal.Transaction

			//fmt.Printf(" ---> %s", string(msg.Value))

			var tx internal.Transaction
			err = json.Unmarshal(msg.Value, &tx)

			//fmt.Printf(" ---> TX %d: %v\n", tx.TRANSACTION_ID, tx)

			// check 1: rules engine
			if err := internal.PostJSON(rulesAppEndpoint, &tx, &resp); err != nil {
				fmt.Printf(" --> rules error: %v\n", err)
				continue // FIXME skipping this transaction, what else?
			}

			// check 2: ML model in case the rules engine passed the TX
			if resp.TX_FRAUD_PREDICTION == 0 {
				if err := internal.PostJSON(fraudAppEndpoint, &tx, &resp); err != nil {
					fmt.Printf(" --> ML error: %v\n", err)
					continue // FIXME skipping this transaction, what else?
				}
			}

			// decide on the target topic based on TX_FRAUD
			if resp.TX_FRAUD_PREDICTION > 0 {
				nextTopic = fraudTopic
				tx.TX_FRAUD = 0 // this is still 0 and might get overwritten by the case_svc
				tx.TX_FRAUD_SCENARIO = resp.TX_FRAUD_SCENARIO
				tx.TX_FRAUD_PREDICTION = resp.TX_FRAUD_PREDICTION
				tx.TX_FRAUD_PROBABILITY = resp.TX_FRAUD_PROBABILITY

			} else {
				// TX seems to be OK, clear the fraud flags
				tx.TX_FRAUD = 0
				tx.TX_FRAUD_SCENARIO = 0
				tx.TX_FRAUD_PREDICTION = 0
				tx.TX_FRAUD_PROBABILITY = 0.0
			}

			if tx.TX_FRAUD_PREDICTION > 0 {
				fmt.Printf(" ---> fraudulent TX %d: %v\n", tx.TRANSACTION_ID, tx)
			}

			// back to a json string
			data, err := json.Marshal(tx)
			if err != nil {
				fmt.Printf(" --> json error: %v\n", err)
				continue // FIXME skipping this transaction, what else?
			}

			// send to the next destination
			err = kp.Produce(&kafka.Message{
				TopicPartition: kafka.TopicPartition{
					Topic:     &nextTopic,
					Partition: kafka.PartitionAny,
				},
				Value: data,
			}, evts)
			if err != nil {
				fmt.Printf(" --> producer error: %v\n", err)
			}

			// metrics
			opsTxProcessed.Inc()

		} else {
			// The client will automatically try to recover from all errors.
			fmt.Printf(" --> consumer error: %v (%v)\n", err, msg)
		}
	}
}
