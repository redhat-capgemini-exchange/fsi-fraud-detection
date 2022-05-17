package internal

import (
	"fmt"
	"os"
	"testing"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"

	"github.com/stretchr/testify/assert"
)

func TestS3Access(t *testing.T) {
	sess, err := session.NewSession(&aws.Config{
		Region: aws.String("eu-central-1")},
	)
	assert.NoError(t, err)
	assert.NotEmpty(t, sess)

	// Create S3 service client
	svc := s3.New(sess)
	assert.NotEmpty(t, svc)

	result, err := svc.ListBuckets(nil)
	assert.NoError(t, err)
	assert.NotEmpty(t, result)

	for _, b := range result.Buckets {
		fmt.Printf("* %s created on %s\n",
			aws.StringValue(b.Name), aws.TimeValue(b.CreationDate))
	}
}

func TestS3Upload(t *testing.T) {
	sess, err := session.NewSession(&aws.Config{
		Region: aws.String("eu-central-1")},
	)
	assert.NoError(t, err)
	assert.NotEmpty(t, sess)

	// Create S3 service client
	uploader := s3manager.NewUploader(sess)
	assert.NotEmpty(t, uploader)

	fileName := "json.go"
	bucketName := "fsi-fraud-detection"

	file, err := os.Open(fileName)
	assert.NoError(t, err)
	defer file.Close()

	_, err = uploader.Upload(&s3manager.UploadInput{
		Bucket: aws.String(bucketName),
		Key:    aws.String("test/" + fileName),
		Body:   file,
	})
	assert.NoError(t, err)
}
