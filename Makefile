PROD_NAMESPACE = fsi-fraud-detection
DEV_NAMESPACE = fsi-fraud-detection-dev
BUILD_NAMESPACE = fsi-fraud-detection-xops

.PHONY: create_namespaces
create_namespaces:
	oc new-project ${PROD_NAMESPACE}
	oc new-project ${DEV_NAMESPACE}
	oc new-project ${BUILD_NAMESPACE}
	oc policy add-role-to-user \
		system:image-puller system:serviceaccount:${PROD_NAMESPACE}:default \
    	--namespace=${BUILD_NAMESPACE}
	oc policy add-role-to-user \
		system:image-puller system:serviceaccount:${PROD_NAMESPACE}:default \
    	--namespace=${DEV_NAMESPACE}
	oc policy add-role-to-user \
		system:image-puller system:serviceaccount:${DEV_NAMESPACE}:default \
    	--namespace=${BUILD_NAMESPACE}

.PHONY: apply_config
apply_config:
	oc apply -f services/deploy/config_fsi_fraud_detection.yaml -n ${BUILD_NAMESPACE}
	oc apply -f services/deploy/config_fsi_fraud_detection.yaml -n ${PROD_NAMESPACE}
	oc apply -f secrets/build_secrets.yaml -n ${BUILD_NAMESPACE}
	oc apply -f secrets/deploy_secrets.yaml -n ${PROD_NAMESPACE}
	
.PHONY: apply_build
apply_build:
	oc apply -f services/deploy/images_fsi_fraud_detection.yaml -n ${BUILD_NAMESPACE}
	oc apply -f services/deploy/build_topic_listener.yaml -n ${BUILD_NAMESPACE}
	oc apply -f services/deploy/build_fraud_detection.yaml -n ${BUILD_NAMESPACE}
	oc apply -f services/deploy/build_archive_svc.yaml -n ${BUILD_NAMESPACE}
	oc apply -f services/deploy/build_case_svc.yaml -n ${BUILD_NAMESPACE}
	oc apply -f services/deploy/build_router_svc.yaml -n ${BUILD_NAMESPACE}
	
.PHONY: apply_deploy
apply_deploy:
	oc apply -f services/deploy/deploy_archive_svc.yaml -n ${PROD_NAMESPACE}
	oc apply -f services/deploy/deploy_case_svc.yaml -n ${PROD_NAMESPACE}
	oc apply -f services/deploy/deploy_data_svc.yaml -n ${PROD_NAMESPACE}
	oc apply -f services/deploy/deploy_router_svc.yaml -n ${PROD_NAMESPACE}

