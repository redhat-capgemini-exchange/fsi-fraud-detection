## Solution deployment

This is a rough step-by-step guide how to deploy the solution. The setup will be automated as we progress but for now it is 
a manual process. The following infrastructure is used:

* Red Hat OpenShift 4.10 (latest)
* Red Hat AMQ Streams, on OpenShift (a.k.a Kafka)
* A project on the Google Cloud Platform, to simulate a 'data-lake'

### Preparation

* create an OpenShift cluster
* create a project on GCP

#### Google Cloud Platform

* create a project: `fsi-fraud-dection`
* create two buckets in Cloud Storage: `fsi-fraud-detection-training` and `fsi-fraud-detection-archive`
* create an service account with the following roles: `Cloud Datastore Owner`, `Cloud Datastore User` and `Cloud Datastore Viewer`
* Download the associated key, it is needed in some of the services to read/write files in the above buckets

#### OpenShift Infrastructure

* create a new OCP 4.10 (as of April 2022) cluster

Install the following Operators:

* Red Hat OpenShift Pipelines
* Red Hat OpenShift GitOps
* Red Hat OpenShift Serverless
* Red Hat Integration - AMQ Streams

Just install the Operators using the defaults and `latest`.
 
### Setup

Create the default project:


```shell
oc new-project fsi-fraud-detection
```

All deployment commands `MUST` be preformed in the context of this project/namespace!

#### Preparation

```shell
oc apply -f deploy/limit-ranges.yaml -n fsi-fraud-detection
```

#### Kafka

```shell
oc apply -f deploy/kafka.yaml -n fsi-fraud-detection

# ... wait until Kafka is ready ...

oc apply -f deploy/kafka-topics.yaml -n fsi-fraud-detection
oc apply -f deploy/kafka-bridge.yaml -n fsi-fraud-detection
oc apply -f deploy/kafka-bridge-route.yaml -n fsi-fraud-detection
```

