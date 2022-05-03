package internal

import (
	"fmt"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func TestTimestampFileName(t *testing.T) {
	layoutISO := "2006-01-02"

	ts := time.Now().UnixNano()
	now := time.Now()

	fmt.Printf("%s-%d\n", now.Format(layoutISO), ts)

	assert.NotEmpty(t, layoutISO)
}
