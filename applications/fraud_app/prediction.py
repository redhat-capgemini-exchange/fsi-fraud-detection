import os
import pandas as pd
import cloudpickle as cp


input_features = ['TX_AMOUNT', 'TX_DURING_WEEKEND', 'TX_DURING_NIGHT', 'CUSTOMER_ID_NB_TX_1DAY_WINDOW',
                  'CUSTOMER_ID_AVG_AMOUNT_1DAY_WINDOW', 'CUSTOMER_ID_NB_TX_7DAY_WINDOW',
                  'CUSTOMER_ID_AVG_AMOUNT_7DAY_WINDOW', 'CUSTOMER_ID_NB_TX_30DAY_WINDOW',
                  'CUSTOMER_ID_AVG_AMOUNT_30DAY_WINDOW', 'TERMINAL_ID_NB_TX_1DAY_WINDOW',
                  'TERMINAL_ID_RISK_1DAY_WINDOW', 'TERMINAL_ID_NB_TX_7DAY_WINDOW',
                  'TERMINAL_ID_RISK_7DAY_WINDOW', 'TERMINAL_ID_NB_TX_30DAY_WINDOW',
                  'TERMINAL_ID_RISK_30DAY_WINDOW']

# load the latest model
model_location = os.getenv('model_location', 'model_latest.pkl')
TX_FRAUD_THRESHOLD = float(os.getenv('tx_fraud_threshold', '0.8'))
TX_FRAUD_SCENARIO = int(os.getenv('tx_fraud_scenario', '2'))

# load the model if possible
print(f" --> loading model '{model_location}'")

model = None
try:
    model = cp.load(open(model_location, 'rb'))
except:
    print(f" --> failed to load model '{model_location}'")


def predict(args_dict):
    scenario = -1
    fraud = 0

    if model == None:
        return {
            'TRANSACTION_ID': args_dict.get('TRANSACTION_ID'),
            'TX_FRAUD_PREDICTION': fraud,
            'TX_FRAUD_PROBABILITY': 0.0,
            'TX_FRAUD_SCENARIO': scenario
        }

    # calculate the fraud probability
    df = pd.DataFrame(args_dict, index=[0])[input_features]
    prob = model.predict_proba(df)

    # build the result set
    p = prob[:, 1][0]
    if p >= TX_FRAUD_THRESHOLD:
        fraud = 1
        scenario = TX_FRAUD_SCENARIO
        print(
            f" --> potential fraudulent TX '{args_dict.get('TRANSACTION_ID')}': {args_dict}")

    return {
        'TRANSACTION_ID': args_dict.get('TRANSACTION_ID'),
        'TX_FRAUD_PREDICTION': fraud,
        'TX_FRAUD_PROBABILITY': p,
        'TX_FRAUD_SCENARIO': scenario
    }
