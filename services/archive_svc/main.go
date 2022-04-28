package main

import (
	"fmt"

	"github.com/confluentinc/confluent-kafka-go/kafka"
	"github.com/txsvc/stdlib/v2/env"
)

func main() {

	kafkaService := env.GetString("kafka_service", "")
	if kafkaService == "" {
		panic(fmt.Errorf("missing env 'kafka_service'"))
	}
	kafkaPort := env.GetString("kafka_port", "9092")
	kafkaServer := fmt.Sprintf("%s:%s", kafkaService, kafkaPort)

	clientID := env.GetString("client_id", "archive-svc")
	groupID := env.GetString("group_id", "fsi-fraud-detection")

	source := env.GetString("source_topic", "tx-archive")

	c, err := kafka.NewConsumer(&kafka.ConfigMap{
		"bootstrap.servers":   kafkaServer,
		"client.id":           clientID,
		"group.id":            groupID,
		"consumer.timeout.ms": -1,
		"auto.offset.reset":   "earliest",
	})

	if err != nil {
		panic(err)
	}

	c.SubscribeTopics([]string{source}, nil)

	for {
		msg, err := c.ReadMessage(-1)
		if err == nil {
			fmt.Printf("Message on %s: %s\n", msg.TopicPartition, string(msg.Value))
		} else {
			// The client will automatically try to recover from all errors.
			fmt.Printf("Consumer error: %v (%v)\n", err, msg)
		}
	}

	c.Close()
}
