import os

TX_FRAUD_THRESHOLD = float(os.getenv('tx_fraud_threshold'))
TX_FRAUD_SCENARIO = int(os.getenv('tx_fraud_scenario'))


def validate(args_dict):

    fraud = 0
    scenario = -1

    amount = args_dict.get('TX_AMOUNT')
    if amount > TX_FRAUD_THRESHOLD:
        fraud = 1
        scenario = TX_FRAUD_SCENARIO
        print(f" --> potential fraudulent tx '{args_dict.get('TRANSACTION_ID')}', amount={amount}")

    return {
        'TRANSACTION_ID': args_dict.get('TRANSACTION_ID'),
        'TX_FRAUD': fraud,
        'TX_FRAUD_SCENARIO': scenario
    }
