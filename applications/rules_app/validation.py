import os

TX_FRAUD_THRESHOLD = float(os.getenv('tx_fraud_threshold', '220.0'))
TX_FRAUD_SCENARIO = int(os.getenv('tx_fraud_scenario', '1'))


def validate(args_dict):
    fraud = 0
    scenario = -1
    prob = 0.0

    amount = args_dict.get('TX_AMOUNT')
    if amount > TX_FRAUD_THRESHOLD:
        fraud = 1
        prob = 1.0
        scenario = TX_FRAUD_SCENARIO
        print(
            f" --> potential fraudulent TX '{args_dict.get('TRANSACTION_ID')}': {args_dict}")

    return {
        'TRANSACTION_ID': args_dict.get('TRANSACTION_ID'),
        'TX_FRAUD_PREDICTION': fraud,
        'TX_FRAUD_PROBABILITY': prob,
        'TX_FRAUD_SCENARIO': scenario
    }
