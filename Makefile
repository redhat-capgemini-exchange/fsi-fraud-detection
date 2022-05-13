PROD_NAMESPACE = fsi-fraud-detection
DEV_NAMESPACE = fsi-fraud-detection-dev
BUILD_NAMESPACE = fsi-fraud-detection-xops

# step1
.PHONY: create_namespaces
create_namespaces:
	oc new-project ${PROD_NAMESPACE}
	oc new-project ${DEV_NAMESPACE}
	oc new-project ${BUILD_NAMESPACE}

# step2
.PHONY: prepare_infra
prepare_infra: config_infra apply_config config_kafka config_monitoring prepare_images

# step3
.PHONY: prepare_build
prepare_build:
	oc apply -f builder/data_svc.yaml -n ${BUILD_NAMESPACE}
	oc apply -f builder/case_svc.yaml -n ${BUILD_NAMESPACE}
	oc apply -f builder/router_svc.yaml -n ${BUILD_NAMESPACE}
	oc apply -f builder/rules_app.yaml -n ${BUILD_NAMESPACE}
	oc apply -f builder/fraud_app.yaml -n ${BUILD_NAMESPACE}
	oc apply -f builder/archive_svc.yaml -n ${BUILD_NAMESPACE}

# step4
.PHONY: deploy_services
deploy_services:
	oc apply -f deploy/services/archive_svc.yaml -n ${PROD_NAMESPACE}
	oc apply -f deploy/services/case_svc.yaml -n ${PROD_NAMESPACE}
	oc apply -f deploy/services/router_svc.yaml -n ${PROD_NAMESPACE}
	oc apply -f deploy/applications/rules_app.yaml -n ${PROD_NAMESPACE}
	oc apply -f deploy/applications/fraud_app.yaml -n ${PROD_NAMESPACE}
	oc apply -f deploy/services/data_svc.yaml -n ${PROD_NAMESPACE}


# basics to prepare the environment and the build tasks

.PHONY: config_infra
config_infra:
	oc apply -f deploy/limit-ranges.yaml -n ${PROD_NAMESPACE}
	oc policy add-role-to-user \
		system:image-puller system:serviceaccount:${PROD_NAMESPACE}:default \
    	--namespace=${BUILD_NAMESPACE}
	oc policy add-role-to-user \
		system:image-puller system:serviceaccount:${PROD_NAMESPACE}:default \
    	--namespace=${DEV_NAMESPACE}
	oc policy add-role-to-user \
		system:image-puller system:serviceaccount:${DEV_NAMESPACE}:default \
    	--namespace=${BUILD_NAMESPACE}
	oc apply -f deploy/pvc_data.yaml -n ${PROD_NAMESPACE}
	oc apply -f deploy/pvc_models.yaml -n ${PROD_NAMESPACE}

.PHONY: apply_config
apply_config:
	oc apply -f deploy/config_fsi_fraud_detection.yaml -n ${BUILD_NAMESPACE}
	oc apply -f deploy/config_fsi_fraud_detection.yaml -n ${PROD_NAMESPACE}
	oc apply -f secrets/build_secrets.yaml -n ${BUILD_NAMESPACE}
	oc apply -f secrets/deploy_secrets.yaml -n ${PROD_NAMESPACE}

.PHONY: config_kafka
config_kafka:
	oc apply -f deploy/kafka/kafka.yaml -n ${PROD_NAMESPACE}
	oc apply -f deploy/kafka/kafka-topics.yaml -n ${PROD_NAMESPACE}
	oc apply -f deploy/kafka/kafka-bridge.yaml -n ${PROD_NAMESPACE}
	oc apply -f deploy/kafka/kafka-bridge-route.yaml -n ${PROD_NAMESPACE}

.PHONY: config_monitoring
config_monitoring:
	oc apply -f deploy/monitoring/cluster_monitoring_config.yaml
	oc apply -f deploy/monitoring/user_workload_monitoring_config.yaml
	
.PHONY: prepare_images
prepare_images:
	oc import-image ubi8/s2i-base:1-343 --from=registry.access.redhat.com/ubi8/s2i-base:1-343 -n ${BUILD_NAMESPACE}
	oc import-image ubi8/s2i-base:latest --from=registry.access.redhat.com/ubi8/s2i-base:1-343 -n ${BUILD_NAMESPACE}
	oc import-image ubi8/python-39:1-51 --from=registry.access.redhat.com/ubi8/python-39:1-51 -n ${BUILD_NAMESPACE}
	oc import-image ubi8/python-39:latest --from=registry.access.redhat.com/ubi8/python-39:1-51 -n ${BUILD_NAMESPACE}
	oc apply -f builder/build_golang_base.yaml -n ${BUILD_NAMESPACE}
	# NOT USED WITH ODH: oc apply -f builder/build_notebook_base.yaml -n ${BUILD_NAMESPACE}


# cleanup tasks

.PHONY: cleanup
cleanup:
	oc delete build --all -n ${BUILD_NAMESPACE}
	oc delete pipelineruns --all -n ${BUILD_NAMESPACE}
	oc delete pod --field-selector=status.phase==Succeeded -n ${BUILD_NAMESPACE}
	oc delete pod --field-selector=status.phase==Succeeded -n ${PROD_NAMESPACE}

.PHONY: undeploy_all
undeploy_all: cleanup
	oc delete routes,dc,pvc,services,configmaps,secrets -l app-owner=fsi-fraud-detection -n ${PROD_NAMESPACE}
	oc delete bc,is,configmaps,secrets -l app-owner=fsi-fraud-detection -n ${BUILD_NAMESPACE}
	oc delete is --all -n ${BUILD_NAMESPACE}

# devops tasks

.PHONY: build_all
build_all:
	oc start-build golang-base -n ${BUILD_NAMESPACE}
	oc start-build data-svc -n ${BUILD_NAMESPACE}
	oc start-build rules-app -n ${BUILD_NAMESPACE}
	oc start-build fraud-app -n ${BUILD_NAMESPACE}

.PHONY: rollout_all
rollout_all: rollout_apps rollout_svc

.PHONY: rollout_svc
rollout_svc:
	oc rollout latest dc/data-svc -n ${PROD_NAMESPACE}
	oc rollout latest dc/router-svc -n ${PROD_NAMESPACE}
	oc rollout latest dc/case-svc -n ${PROD_NAMESPACE}
	oc rollout latest dc/archive-svc -n ${PROD_NAMESPACE}

.PHONY: rollout_apps
rollout_apps:
	oc rollout latest dc/fraud-app -n ${PROD_NAMESPACE}
	oc rollout latest dc/rules-app -n ${PROD_NAMESPACE}

#
# DEPRECATED
#

.PHONY: deploy_notebooks
deploy_notebooks:
	oc apply -f notebooks/deploy_simulator_notebook.yaml -n ${PROD_NAMESPACE}
	
.PHONY: prepare_notebooks
prepare_notebooks:
	oc apply -f notebooks/notebook_secrets.yaml -n ${PROD_NAMESPACE}
	oc apply -f notebooks/build_simulator_notebook.yaml -n ${BUILD_NAMESPACE}
