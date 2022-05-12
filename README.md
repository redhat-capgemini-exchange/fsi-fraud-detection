# fsi-fraud-detection

Setup of a basic MLOps demonstrator inspired by the "[Reproducible Machine Learning for Credit Card Fraud Detection - Practical Handbook](https://fraud-detection-handbook.github.io/fraud-detection-handbook/Foreword.html)" repository on GitHub.

## Deployment

See deploy/README.md

## Run the demo

### Deploy the notebooks

```shell
make deploy_notebooks
```

### Run the notebooks

To create synthetic data:

* 01_create_transactions.ipynb
* 02_feature_transformation.ipynb

To create a first ML model:

* 03_train_model.ipynb

Note: Stop the notebook server after creating the data !

### References

* [Fraud detection with machine learning](https://www.researchgate.net/project/Fraud-detection-with-machine-learning)
* [Reproducible Machine Learning for Credit Card Fraud Detection - Practical Handbook](https://fraud-detection-handbook.github.io/fraud-detection-handbook/Foreword.html)
* [https://github.com/Fraud-Detection-Handbook/fraud-detection-handbook](https://github.com/Fraud-Detection-Handbook/fraud-detection-handbook)

### APIs and modules

* [https://pkg.go.dev/github.com/confluentinc/confluent-kafka-go@v1.8.2/kafka](confluent-kafka-go )
* [https://github.com/googleapis/python-storage](googleapis python-storage)
* [https://cloud.google.com/storage/docs/reference/libraries#client-libraries-install-python](Cloud Storage client libraries)

### Local development

#### Python virtual environment

```shell
pip install virtualenv

python3 -m venv venv

source env/bin/activate

...

deactivate

```

#### Install packages

```shell
pip install -r requirements.txt
```
