package main

import (
	"encoding/csv"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"time"

	"github.com/confluentinc/confluent-kafka-go/kafka"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
	"github.com/prometheus/client_golang/prometheus/promhttp"

	"github.com/txsvc/stdlib/v2/env"

	"github.com/redhat-capgemini-exchange/fsi-fraud-detection/internal"
)

const (
	layoutISO = "2006-01-02"
)

func main() {

	// kafka setup
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
	archiveLocationPrefix := env.GetString("target_prefix", "audit")

	// prometheus setup
	promHost := env.GetString("prom_host", "0.0.0.0:2112")
	promMetricsPath := env.GetString("prom_metrics_path", "/metrics")

	opsTxProcessed := promauto.NewCounter(prometheus.CounterOpts{
		Name: "fraud_processed_transactions",
		Help: "The number of processed transactions",
	})

	// start the metrics listener
	go func() {
		fmt.Printf(" --> starting metrics endpoint '%s' on '%s'\n", promMetricsPath, promHost)

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

	err = kc.SubscribeTopics([]string{sourceTopic}, nil)
	if err != nil {
		panic(err)
	}

	fmt.Printf(" --> %s: listening on topic '%s'\n", clientID, sourceTopic)

	// setup the next .csv file
	out, location := newFile(archiveLocation, archiveLocationPrefix)
	writer := csv.NewWriter(out)
	writer.Write(internal.ArchiveHeader)
	batchSize := 1000
	num := 0

	fmt.Printf(" --> archiving to %s\n", location)

	for {
		msg, err := kc.ReadMessage(-1)
		if err == nil {
			var tx internal.Transaction
			err = json.Unmarshal(msg.Value, &tx)
			writer.Write(tx.ToArray())

			// metrics
			num++
			opsTxProcessed.Inc()

			// start a new file every ... tx
			if num%batchSize == 0 {
				// close-of the current file
				writer.Flush()
				out.Close()
				// start the new batcg
				num = 0
				out, location = newFile(archiveLocation, archiveLocationPrefix)
				writer = csv.NewWriter(out)
				writer.Write(internal.ArchiveHeader)

				fmt.Printf(" --> archiving to %s\n", location)
			}
		} else {
			// The client will automatically try to recover from all errors.
			fmt.Printf(" --> consumer error: %v (%v)\n", err, msg)
		}
	}

}

func newFile(path, prefix string) (*os.File, string) {
	location := filepath.Join(path, prefix)
	if _, err := os.Stat(location); os.IsNotExist(err) {
		err := os.Mkdir(location, os.ModePerm)
		if err != nil {
			panic(err)
		}
	}

	fullPath := filepath.Join(location, timestampFileName())
	out, err := os.Create(fullPath)
	if err != nil {
		panic(err)
	}
	return out, fullPath
}

func timestampFileName() string {
	ts := time.Now().UnixNano()
	now := time.Now()

	return fmt.Sprintf("%s-%d.csv", now.Format(layoutISO), ts)
}
