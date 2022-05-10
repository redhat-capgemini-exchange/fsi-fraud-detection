## Solution deployment

This is a rough step-by-step guide how to deploy the solution. The setup will be automated as we progress but for now it is 
a manual process. The following infrastructure is used:

* Red Hat OpenShift 4.10 (latest)
* Red Hat AMQ Streams, on OpenShift (a.k.a Kafka)
* A project on the Google Cloud Platform, to simulate a 'data-lake'

### Preparation

* create an OpenShift cluster
* create a project on GCP (optional)

#### Google Cloud Platform (optional)

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

Step 1: Create the default projects and basic infrastructure:

```shell
make prepare
```

* In project `fsi-fraud-detection`, wait until the Kafka resources (Broker, Zookeeper, Bridge) are ready.
* In project `fsi-fraud-detection-xops`, verify that the `golang` and `Jupyter` s2i images are created.

Step 2: Create all services and apps

```shell
make prepare_build
```

* In project `fsi-fraud-detection-xops`, wait until all builds are completed.

