package main

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/confluentinc/confluent-kafka-go/kafka"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
	"github.com/prometheus/client_golang/prometheus/promhttp"

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
	targetTopic := env.GetString("target_topic", "tx-archive")

	// prometheus setup
	promHost := env.GetString("prom_host", "0.0.0.0:2112")
	promMetricsPath := env.GetString("prom_metrics_path", "/metrics")

	opsTxProcessed := promauto.NewCounter(prometheus.CounterOpts{
		Name: "fraud_case_svc_txs",
		Help: "The number of processed transactions",
	})

	// start the metrics listener
	go func() {
		http.Handle(promMetricsPath, promhttp.Handler())
		http.ListenAndServe(promHost, nil)
	}()

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
					Topic:     &targetTopic,
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
