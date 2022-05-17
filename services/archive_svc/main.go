package main

import (
	"encoding/csv"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
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

var (
	kc             *kafka.Consumer
	opsTxProcessed prometheus.Counter
	uploader       *s3manager.Uploader
)

func init() {

	// kafka setup
	kafkaService := env.GetString("kafka_service", "")
	if kafkaService == "" {
		panic(fmt.Errorf("missing env 'kafka_service'"))
	}
	kafkaServicePort := env.GetString("kafka_service_port", "9092")
	kafkaServer := fmt.Sprintf("%s:%s", kafkaService, kafkaServicePort)

	clientID := env.GetString("client_id", "archive-svc")
	groupID := env.GetString("group_id", "fsi-fraud-detection")

	// https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
	k, err := kafka.NewConsumer(&kafka.ConfigMap{
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
	kc = k

	// AWS S3 setup
	region := env.GetString("aws_region", "eu-central-1")
	sess, err := session.NewSession(&aws.Config{
		Region: aws.String(region)},
	)
	if err != nil {
		panic(err)
	}
	uploader = s3manager.NewUploader(sess)

	// metrics collectors
	opsTxProcessed = promauto.NewCounter(prometheus.CounterOpts{
		Name: "fraud_processed_transactions",
		Help: "The number of processed transactions",
	})

	// prometheus endpoint setup
	promHost := env.GetString("prom_host", "0.0.0.0:2112")
	promMetricsPath := env.GetString("prom_metrics_path", "/metrics")

	// start the metrics listener
	go func() {
		fmt.Printf(" --> starting metrics endpoint '%s' on '%s'\n", promMetricsPath, promHost)

		http.Handle(promMetricsPath, promhttp.Handler())
		http.ListenAndServe(promHost, nil)
	}()
}

func main() {
	// local path in PVC
	archiveLocation := env.GetString("target_location", "/opt/app-root/data")
	archiveLocationPrefix := env.GetString("target_prefix", "audit")

	// batch size
	batchSize := int(env.GetInt("batch_size", 1000))

	// start listening on the kafka topic
	sourceTopic := env.GetString("source_topic", "tx-archive")
	err := kc.SubscribeTopics([]string{sourceTopic}, nil)
	if err != nil {
		panic(err)
	}

	clientID := env.GetString("client_id", "archive-svc")
	fmt.Printf(" --> %s: listening on topic '%s'\n", clientID, sourceTopic)

	// setup the next .csv file
	out, location := newFile(archiveLocation, archiveLocationPrefix)
	writer := csv.NewWriter(out)
	writer.Write(internal.ArchiveHeader)
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
				// close the current file
				writer.Flush()
				out.Close()

				// upload the file in the background
				go upload(location)

				// start the new batch
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

func upload(path string) {
	locationPrefix := env.GetString("target_prefix", "audit")
	bucketName := env.GetString("aws_bucket", "fsi-fraud-detection")

	filename := filepath.Base(path)
	location := fmt.Sprintf("%s/%s", locationPrefix, filename)

	file, err := os.Open(path)
	if err != nil {
		fmt.Printf(" --> unable to upload '%s':%v\n", path, err)
		return
	}
	defer file.Close()

	fmt.Printf(" --> uploading '%s' to 's3://%s/%s'\n", filename, bucketName, location)

	_, err = uploader.Upload(&s3manager.UploadInput{
		Bucket: aws.String(bucketName),
		Key:    aws.String(location),
		Body:   file,
	})
	if err != nil {
		fmt.Printf(" --> failed to upload '%s':%v\n", path, err)
		return
	}
}
