package main

import (
	"encoding/csv"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"time"

	"github.com/confluentinc/confluent-kafka-go/kafka"
	"github.com/txsvc/stdlib/v2/env"

	"github.com/redhat-capgemini-exchange/fsi-fraud-detection/internal"
)

const (
	layoutISO = "2006-01-02"
)

func main() {

	kafkaService := env.GetString("kafka_service", "")
	if kafkaService == "" {
		panic(fmt.Errorf("missing env 'kafka_service'"))
	}
	kafkaServicePort := env.GetString("kafka_service_port", "9092")
	kafkaServer := fmt.Sprintf("%s:%s", kafkaService, kafkaServicePort)

	clientID := env.GetString("client_id", "archive-svc")
	groupID := env.GetString("group_id", "fsi-fraud-detection")

	sourceTopic := env.GetString("source_topic", "tx-archive")
	archiveLocation := env.GetString("target_location", "/opt/app-root/data")
	archiveLocationPrefix := env.GetString("target_prefix", "archive")

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

	//sigchan := make(chan os.Signal, 1)
	//signal.Notify(sigchan, syscall.SIGINT, syscall.SIGTERM)

	err = kc.SubscribeTopics([]string{sourceTopic}, nil)
	if err != nil {
		panic(err)
	}

	fmt.Printf(" --> %s: listening on topic '%s'\n", clientID, sourceTopic)

	// setup the next .csv file
	out, location := newFile(archiveLocation, archiveLocationPrefix)
	writer := csv.NewWriter(out)
	writer.Write(internal.ArchiveHeader)
	batchSize := 100
	num := 0

	fmt.Printf(" ---> archiving to %s\n", location)

	for {
		msg, err := kc.ReadMessage(-1)
		if err == nil {
			var tx internal.Transaction
			err = json.Unmarshal(msg.Value, &tx)

			//fmt.Printf(" ---> message on %s: %v\n", msg.TopicPartition, tx)
			num++
			writer.Write(tx.ToArray())

			if num%batchSize == 0 {
				// close-of the current file
				writer.Flush()
				out.Close()
				// start the new batcg
				num = 0
				out, location = newFile(archiveLocation, archiveLocationPrefix)
				writer = csv.NewWriter(out)
				writer.Write(internal.ArchiveHeader)

				fmt.Printf(" ---> archiving to %s\n", location)
			}
		} else {
			// The client will automatically try to recover from all errors.
			fmt.Printf(" --> consumer error: %v (%v)\n", err, msg)
		}
	}

	//c.Close()
}

func newFile(path, prefix string) (*os.File, string) {
	location := filepath.Join(path, prefix, timestampFileName())
	out, err := os.Create(location)
	if err != nil {
		panic(err)
	}
	return out, location
}

func timestampFileName() string {
	ts := time.Now().UnixNano()
	now := time.Now()

	return fmt.Sprintf("%s-%d.csv", now.Format(layoutISO), ts)
}
