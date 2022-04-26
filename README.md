# fsi-fraud-detection

Setup of a basic MLOps demonstrator inspired by the "Reproducible Machine Learning for Credit Card Fraud Detection - Practical Handbook" repository on GitHub.

### References

* [Reproducible Machine Learning for Credit Card Fraud Detection - Practical Handbook](https://fraud-detection-handbook.github.io/fraud-detection-handbook/Foreword.html)
* [https://github.com/Fraud-Detection-Handbook/fraud-detection-handbook](https://github.com/Fraud-Detection-Handbook/fraud-detection-handbook)










### OpenShift and Operators

* OpenShift 4.9.22

#### Basics

* Red Hat CodeReady Workspaces 2.15.2
* Web Terminal 1.4.0
* Red Hat OpenShift Pipelines 1.6.2
* Red Hat OpenShift GitOps 1.4.5

* Red Hat OpenShift Serverless 1.21.0
* Red Hat Integration - AMQ Streams 2.0.1-2

* Red Hat Prometheus Operator 0.47.0

* Open Data Hub Operator 1.1.2
* Seldon Operator 1.12.0


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
