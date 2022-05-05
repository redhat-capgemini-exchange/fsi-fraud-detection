PROD_NAMESPACE = fsi-fraud-detection
DEV_NAMESPACE = fsi-fraud-detection-dev
BUILD_NAMESPACE = fsi-fraud-detection-xops

.PHONY: prepare
prepare: create_namespaces config_system deploy_kafka

.PHONY: prepare_build
prepare_build: apply_config apply_build prepare_notebooks

.PHONY: prepare_notebooks
prepare_notebooks:
	oc apply -f notebooks/build_simulator_notebook.yaml -n ${BUILD_NAMESPACE}
	oc apply -f notebooks/deploy_simulator_notebook.yaml -n ${PROD_NAMESPACE}

.PHONY: create_namespaces
create_namespaces:
	oc new-project ${PROD_NAMESPACE}
	oc new-project ${DEV_NAMESPACE}
	oc new-project ${BUILD_NAMESPACE}

.PHONY: config_system
config_system:
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
	oc apply -f deploy/pvc_fsi_fraud_detection.yaml -n ${PROD_NAMESPACE}

.PHONY: deploy_kafka
deploy_kafka:
	oc apply -f deploy/kafka.yaml -n ${PROD_NAMESPACE}
	oc apply -f deploy/kafka-topics.yaml -n ${PROD_NAMESPACE}
	oc apply -f deploy/kafka-bridge.yaml -n ${PROD_NAMESPACE}
	oc apply -f deploy/kafka-bridge-route.yaml -n ${PROD_NAMESPACE}

.PHONY: apply_config
apply_config:
	oc apply -f deploy/config_fsi_fraud_detection.yaml -n ${BUILD_NAMESPACE}
	oc apply -f deploy/config_fsi_fraud_detection.yaml -n ${PROD_NAMESPACE}
	oc apply -f secrets/build_secrets.yaml -n ${BUILD_NAMESPACE}
	oc apply -f secrets/deploy_secrets.yaml -n ${PROD_NAMESPACE}
	
.PHONY: apply_build
apply_build:
	oc apply -f deploy/images_fsi_fraud_detection.yaml -n ${BUILD_NAMESPACE}
	oc apply -f builder/build_golang_custom.yaml -n ${BUILD_NAMESPACE}
	oc apply -f builder/build_data_svc.yaml -n ${BUILD_NAMESPACE}
	oc apply -f builder/build_archive_svc.yaml -n ${BUILD_NAMESPACE}
	oc apply -f builder/build_case_svc.yaml -n ${BUILD_NAMESPACE}
	oc apply -f builder/build_router_svc.yaml -n ${BUILD_NAMESPACE}
	
.PHONY: apply_deploy
apply_deploy:
	oc apply -f deploy/deploy_archive_svc.yaml -n ${PROD_NAMESPACE}
	oc apply -f deploy/deploy_case_svc.yaml -n ${PROD_NAMESPACE}
	oc apply -f deploy/deploy_data_svc.yaml -n ${PROD_NAMESPACE}
	oc apply -f deploy/deploy_router_svc.yaml -n ${PROD_NAMESPACE}

.PHONY: cleanup
cleanup:
	oc delete build --all -n ${BUILD_NAMESPACE}
	oc delete pod --field-selector=status.phase==Succeeded -n ${BUILD_NAMESPACE}
	oc delete pod --field-selector=status.phase==Succeeded -n ${PROD_NAMESPACE}