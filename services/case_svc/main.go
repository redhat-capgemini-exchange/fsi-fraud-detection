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

	source := env.GetString("source_topic", "tx-fraud")
	target := env.GetString("target_topic", "tx-archive")

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

	err = kc.SubscribeTopics([]string{source}, nil)
	if err != nil {
		panic(err)
	}

	fmt.Printf(" --> %s: listening on topic '%s'\n", clientID, source)

	// create a responder for delivery notifications
	evts := make(chan kafka.Event, 1000) // FIXME not sure if such a number is needed ...
	go func() {
		e := <-evts

		switch ev := e.(type) {
		case *kafka.Message:
			if ev.TopicPartition.Error != nil {
				fmt.Printf("Delivery failed: %v\n", ev.TopicPartition)
			} else {
				fmt.Printf("Delivered message to %v\n", ev.TopicPartition)
			}
		}
	}()

	for {
		msg, err := kc.ReadMessage(-1)
		if err == nil {
			var tx internal.Transaction
			err = json.Unmarshal(msg.Value, &tx)

			fmt.Printf(" ---> message on %s: %v\n", msg.TopicPartition, tx)

			// back to a json string
			data, err := json.Marshal(tx)
			if err != nil {
				// do something
			}

			// send to the next destination
			err = kp.Produce(&kafka.Message{
				TopicPartition: kafka.TopicPartition{
					Topic:     &target,
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
