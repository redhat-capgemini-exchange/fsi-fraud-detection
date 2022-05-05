package main

import (
	"encoding/json"
	"fmt"

	"github.com/confluentinc/confluent-kafka-go/kafka"
	"github.com/txsvc/stdlib/v2/env"

	"github.com/redhat-capgemini-exchange/fsi-fraud-detection/internal"
)

func main() {

	kafkaService := env.GetString("kafka_service", "")
	if kafkaService == "" {
		panic(fmt.Errorf("missing env 'kafka_service'"))
	}
	kafkaServicePort := env.GetString("kafka_service_port", "9092")
	kafkaServer := fmt.Sprintf("%s:%s", kafkaService, kafkaServicePort)

	clientID := env.GetString("client_id", "case-svc")
	groupID := env.GetString("group_id", "fsi-fraud-detection")

	sourceTopic := env.GetString("source_topic", "tx-fraud")
	archiveTopic := env.GetString("archive_topic", "tx-archive")
	fraudTopic := env.GetString("fraud_topic", "tx-fraud")

	rulesAppEndpoint := env.GetString("rules_app_svc", "http://rules-app-svc.fsi-fraud-detection.svc.cluster.local:8080/validate")
	//fraudAppEndpoint := env.GetString("fraud_app_svc", "http://fraud-app-svc.fsi-fraud-detection.svc.cluster.local:8080/validate")

	// https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
	kc, err := kafka.NewConsumer(&kafka.ConfigMap{
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

	kp, err := kafka.NewProducer(&kafka.ConfigMap{
		"bootstrap.servers": kafkaServer,
	})
	if err != nil {
		panic(err)
	}

	//sigchan := make(chan os.Signal, 1)
	//signal.Notify(sigchan, syscall.SIGINT, syscall.SIGTERM)

	err = kc.SubscribeTopics([]string{sourceTopic}, nil)
	if err != nil {
		panic(err)
	}

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

	fmt.Printf(" --> %s: listening on topic '%s'\n", clientID, sourceTopic)

	for {
		msg, err := kc.ReadMessage(-1)
		if err == nil {
			nextTopic := archiveTopic

			var tx internal.Transaction
			err = json.Unmarshal(msg.Value, &tx)

			// check 1: rules engine
			var resp internal.Transaction
			if err := internal.PostJSON(rulesAppEndpoint, &tx, &resp); err != nil {
				fmt.Printf(" --> rules error: %v\n", err)
				continue // FIXME skipping this transaction, what else?
			}

			// check 2: ML model
			// TBD

			// decide on the target topic based on TX_FRAUD
			if resp.TX_FRAUD > 0 {
				nextTopic = fraudTopic
				tx.TX_FRAUD = resp.TX_FRAUD
				tx.TX_FRAUD_SCENARIO = resp.TX_FRAUD_SCENARIO
			}

			if tx.TX_FRAUD > 0 {
				fmt.Printf(" ---> fraudulent TX %d: %v\n", tx.TRANSACTION_ID, tx)
			}

			// back to a json string
			data, err := json.Marshal(tx)
			if err != nil {
				// do something
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

		} else {
			// The client will automatically try to recover from all errors.
			fmt.Printf(" --> consumer error: %v (%v)\n", err, msg)
		}
	}
}
