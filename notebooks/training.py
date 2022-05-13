import os
import time
import datetime
import pandas as pd

from sklearn.tree import DecisionTreeClassifier


# Compute the number of transactions per day, fraudulent transactions per day and fraudulent cards per day
def get_tx_stats(transactions_df, start_date_df="2020-04-01"):

    # Number of transactions per day
    nb_tx_per_day = transactions_df.groupby(
        ['TX_TIME_DAYS'])['CUSTOMER_ID'].count()
    # Number of fraudulent transactions per day
    nb_fraudulent_transactions_per_day = transactions_df.groupby(['TX_TIME_DAYS'])[
        'TX_FRAUD'].sum()
    # Number of compromised cards per day
    nb_compromised_cards_per_day = transactions_df[transactions_df['TX_FRAUD'] == 1].groupby(
        ['TX_TIME_DAYS']).CUSTOMER_ID.nunique()

    tx_stats = pd.DataFrame({"nb_tx_per_day": nb_tx_per_day,
                             "nb_fraudulent_transactions_per_day": nb_fraudulent_transactions_per_day,
                            "nb_compromised_cards_per_day": nb_compromised_cards_per_day})

    tx_stats = tx_stats.reset_index()

    start_date = datetime.datetime.strptime(start_date_df, "%Y-%m-%d")
    tx_date = start_date+tx_stats['TX_TIME_DAYS'].apply(datetime.timedelta)

    tx_stats['tx_date'] = tx_date

    return tx_stats


def get_train_test_set(transactions_df, start_date_training, delta_train=7, delta_delay=7, delta_test=7):

    # Get the training set data
    train_df = transactions_df[(transactions_df.TX_DATETIME >= start_date_training) &
                               (transactions_df.TX_DATETIME < start_date_training+datetime.timedelta(days=delta_train))]

    # Get the test set data
    test_df = []

    # Note: Cards known to be compromised after the delay period are removed from the test set
    # That is, for each test day, all frauds known at (test_day-delay_period) are removed

    # First, get known defrauded customers from the training set
    known_defrauded_customers = set(
        train_df[train_df.TX_FRAUD == 1].CUSTOMER_ID)

    # Get the relative starting day of training set (easier than TX_DATETIME to collect test data)
    start_tx_time_days_training = train_df.TX_TIME_DAYS.min()

    # Then, for each day of the test set
    for day in range(delta_test):

        # Get test data for that day
        test_df_day = transactions_df[transactions_df.TX_TIME_DAYS == start_tx_time_days_training +
                                      delta_train+delta_delay +
                                      day]

        # Compromised cards from that test day, minus the delay period, are added to the pool of known defrauded customers
        test_df_day_delay_period = transactions_df[transactions_df.TX_TIME_DAYS == start_tx_time_days_training +
                                                   delta_train +
                                                   day-1]

        new_defrauded_customers = set(
            test_df_day_delay_period[test_df_day_delay_period.TX_FRAUD == 1].CUSTOMER_ID)
        known_defrauded_customers = known_defrauded_customers.union(
            new_defrauded_customers)

        test_df_day = test_df_day[~test_df_day.CUSTOMER_ID.isin(
            known_defrauded_customers)]

        test_df.append(test_df_day)

    test_df = pd.concat(test_df)

    # Sort data sets by ascending order of transaction ID
    train_df = train_df.sort_values('TRANSACTION_ID')
    test_df = test_df.sort_values('TRANSACTION_ID')

    return (train_df, test_df)


def fit_model_and_get_predictions(classifier, train_df, test_df,
                                  input_features, output_feature="TX_FRAUD", scale=True):

    # By default, scales input data
    if scale:
        (train_df, test_df) = scaleData(train_df, test_df, input_features)

    # We first train the classifier using the `fit` method, and pass as arguments the input and output features
    start_time = time.time()
    classifier.fit(train_df[input_features], train_df[output_feature])
    training_execution_time = time.time()-start_time

    # We then get the predictions on the training and test data using the `predict_proba` method
    # The predictions are returned as a numpy array, that provides the probability of fraud for each transaction
    start_time = time.time()
    predictions_test = classifier.predict_proba(test_df[input_features])[:, 1]
    prediction_execution_time = time.time()-start_time

    predictions_train = classifier.predict_proba(
        train_df[input_features])[:, 1]

    # The result is returned as a dictionary containing the fitted models,
    # and the predictions on the training and test sets
    model_and_predictions_dictionary = {'classifier': classifier,
                                        'predictions_test': predictions_test,
                                        'predictions_train': predictions_train,
                                        'training_execution_time': training_execution_time,
                                        'prediction_execution_time': prediction_execution_time
                                        }

    return model_and_predictions_dictionary
