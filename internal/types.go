package internal

import "fmt"

/*
IDX,TRANSACTION_ID,TX_DATETIME,CUSTOMER_ID,TERMINAL_ID,TX_AMOUNT,
0,0,2020-04-01 00:00:31,596,3156,57.16,

TX_TIME_SECONDS,TX_TIME_DAYS,TX_FRAUD,TX_FRAUD_SCENARIO,TX_DURING_WEEKEND,TX_DURING_NIGHT,
31,0,0,0,0,1

CUSTOMER_ID_NB_TX_1DAY_WINDOW,CUSTOMER_ID_AVG_AMOUNT_1DAY_WINDOW,CUSTOMER_ID_NB_TX_7DAY_WINDOW,CUSTOMER_ID_AVG_AMOUNT_7DAY_WINDOW,CUSTOMER_ID_NB_TX_30DAY_WINDOW,CUSTOMER_ID_AVG_AMOUNT_30DAY_WINDOW,TERMINAL_ID_NB_TX_1DAY_WINDOW,TERMINAL_ID_RISK_1DAY_WINDOW,TERMINAL_ID_NB_TX_7DAY_WINDOW,TERMINAL_ID_RISK_7DAY_WINDOW,TERMINAL_ID_NB_TX_30DAY_WINDOW,TERMINAL_ID_RISK_30DAY_WINDOW
1.0,57.16,1.0,57.16,1.0,57.16,0.0,0.0,0.0,0.0,0.0,0.0


*/

type (
	Transaction struct {
		// basic TX data
		TRANSACTION_ID  int64
		TX_DATETIME     int64
		CUSTOMER_ID     int
		TERMINAL_ID     int
		TX_AMOUNT       float64
		TX_TIME_SECONDS int
		TX_TIME_DAYS    int
		// from the simulator
		TX_FRAUD          int
		TX_FRAUD_SCENARIO int
		// data supporting the ML training
		TX_DURING_WEEKEND int
		TX_DURING_NIGHT   int
		// customer RFM (Recency, Frequency, Monetary value)
		CUSTOMER_ID_NB_TX_1DAY_WINDOW       float64
		CUSTOMER_ID_AVG_AMOUNT_1DAY_WINDOW  float64
		CUSTOMER_ID_NB_TX_7DAY_WINDOW       float64
		CUSTOMER_ID_AVG_AMOUNT_7DAY_WINDOW  float64
		CUSTOMER_ID_NB_TX_30DAY_WINDOW      float64
		CUSTOMER_ID_AVG_AMOUNT_30DAY_WINDOW float64
		// terminal risk data
		TERMINAL_ID_NB_TX_1DAY_WINDOW  float64
		TERMINAL_ID_RISK_1DAY_WINDOW   float64
		TERMINAL_ID_NB_TX_7DAY_WINDOW  float64
		TERMINAL_ID_RISK_7DAY_WINDOW   float64
		TERMINAL_ID_NB_TX_30DAY_WINDOW float64
		TERMINAL_ID_RISK_30DAY_WINDOW  float64
		// prediction data, used to evaluate the model performance
		TX_FRAUD_PREDICTION  int
		TX_FRAUD_PROBABILITY float64
	}
)

var (
	ArchiveHeader = []string{
		"TRANSACTION_ID",
		"TX_DATETIME",
		"CUSTOMER_ID",
		"TERMINAL_ID",
		"TX_AMOUNT",
		"TX_TIME_SECONDS",
		"TX_TIME_DAYS",
		"TX_FRAUD",
		"TX_FRAUD_SCENARIO",
		"TX_DURING_WEEKEND",
		"TX_DURING_NIGHT",
		"CUSTOMER_ID_NB_TX_1DAY_WINDOW",
		"CUSTOMER_ID_AVG_AMOUNT_1DAY_WINDOW",
		"CUSTOMER_ID_NB_TX_7DAY_WINDOW",
		"CUSTOMER_ID_AVG_AMOUNT_7DAY_WINDOW",
		"CUSTOMER_ID_NB_TX_30DAY_WINDOW",
		"CUSTOMER_ID_AVG_AMOUNT_30DAY_WINDOW",
		"TERMINAL_ID_NB_TX_1DAY_WINDOW",
		"TERMINAL_ID_RISK_1DAY_WINDOW",
		"TERMINAL_ID_NB_TX_7DAY_WINDOW",
		"TERMINAL_ID_RISK_7DAY_WINDOW",
		"TERMINAL_ID_NB_TX_30DAY_WINDOW",
		"TERMINAL_ID_RISK_30DAY_WINDOW",
		"TX_FRAUD_PREDICTION",
		"TX_FRAUD_PROBABILITY",
	}
)

func (tx *Transaction) ToArray() []string {
	return []string{
		fmt.Sprintf("%d", tx.TRANSACTION_ID),
		fmt.Sprintf("%d", tx.TX_DATETIME),
		fmt.Sprintf("%d", tx.CUSTOMER_ID),                         //"CUSTOMER_ID",
		fmt.Sprintf("%d", tx.TERMINAL_ID),                         //"TERMINAL_ID",
		fmt.Sprintf("%f", tx.TX_AMOUNT),                           //"TX_AMOUNT",
		fmt.Sprintf("%d", tx.TX_TIME_SECONDS),                     //"TX_TIME_SECONDS",
		fmt.Sprintf("%d", tx.TX_TIME_DAYS),                        //"TX_TIME_DAYS",
		fmt.Sprintf("%d", tx.TX_FRAUD),                            //"TX_FRAUD",
		fmt.Sprintf("%d", tx.TX_FRAUD_SCENARIO),                   //"TX_FRAUD_SCENARIO",
		fmt.Sprintf("%d", tx.TX_DURING_WEEKEND),                   //"TX_DURING_WEEKEND",
		fmt.Sprintf("%d", tx.TX_DURING_NIGHT),                     //"TX_DURING_NIGHT",
		fmt.Sprintf("%f", tx.CUSTOMER_ID_NB_TX_1DAY_WINDOW),       //"CUSTOMER_ID_NB_TX_1DAY_WINDOW",
		fmt.Sprintf("%f", tx.CUSTOMER_ID_AVG_AMOUNT_1DAY_WINDOW),  //"CUSTOMER_ID_AVG_AMOUNT_1DAY_WINDOW",
		fmt.Sprintf("%f", tx.CUSTOMER_ID_NB_TX_7DAY_WINDOW),       //"CUSTOMER_ID_NB_TX_7DAY_WINDOW",
		fmt.Sprintf("%f", tx.CUSTOMER_ID_AVG_AMOUNT_7DAY_WINDOW),  //"CUSTOMER_ID_AVG_AMOUNT_7DAY_WINDOW",
		fmt.Sprintf("%f", tx.CUSTOMER_ID_NB_TX_30DAY_WINDOW),      //"CUSTOMER_ID_NB_TX_30DAY_WINDOW",
		fmt.Sprintf("%f", tx.CUSTOMER_ID_AVG_AMOUNT_30DAY_WINDOW), //"CUSTOMER_ID_AVG_AMOUNT_30DAY_WINDOW",
		fmt.Sprintf("%f", tx.TERMINAL_ID_NB_TX_1DAY_WINDOW),       //"TERMINAL_ID_NB_TX_1DAY_WINDOW",
		fmt.Sprintf("%f", tx.TERMINAL_ID_RISK_1DAY_WINDOW),        //"TERMINAL_ID_RISK_1DAY_WINDOW",
		fmt.Sprintf("%f", tx.TERMINAL_ID_NB_TX_7DAY_WINDOW),       //"TERMINAL_ID_NB_TX_7DAY_WINDOW",
		fmt.Sprintf("%f", tx.TERMINAL_ID_RISK_7DAY_WINDOW),        //"TERMINAL_ID_RISK_7DAY_WINDOW",
		fmt.Sprintf("%f", tx.TERMINAL_ID_NB_TX_30DAY_WINDOW),      //"TERMINAL_ID_NB_TX_30DAY_WINDOW",
		fmt.Sprintf("%f", tx.TERMINAL_ID_RISK_30DAY_WINDOW),       //"TERMINAL_ID_RISK_30DAY_WINDOW",
		fmt.Sprintf("%d", tx.TX_FRAUD_PREDICTION),                 //"TX_FRAUD_PREDICTION",
		fmt.Sprintf("%f", tx.TX_FRAUD_PROBABILITY),                //"TX_FRAUD_PROBABILITY",
	}
}
