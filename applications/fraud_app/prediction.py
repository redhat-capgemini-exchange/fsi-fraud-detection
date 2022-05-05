
def predict(args_dict):
    fraud = 0
    scenario = -1

    return {
        'TRANSACTION_ID': args_dict.get('TRANSACTION_ID'),
        'TX_FRAUD': fraud,
        'TX_FRAUD_SCENARIO': scenario
    }
