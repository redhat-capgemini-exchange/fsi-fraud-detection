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
prepare_infra: config_infra apply_config config_kafka prepare_images config_monitoring
#oc apply -f deploy/open-data-hub.yaml -n ${DEV_NAMESPACE}

# step3
.PHONY: prepare_build
prepare_build:
	oc apply -f builder/services/archive.yaml -n ${BUILD_NAMESPACE}
	oc apply -f builder/demo/bridge.yaml -n ${BUILD_NAMESPACE}
	oc apply -f builder/services/case_svc.yaml -n ${BUILD_NAMESPACE}
	oc apply -f builder/services/fraud_svc.yaml -n ${BUILD_NAMESPACE}
	oc apply -f builder/applications/rules_app.yaml -n ${BUILD_NAMESPACE}
	oc apply -f builder/applications/fraud_app.yaml -n ${BUILD_NAMESPACE}

# step4
.PHONY: deploy_services
deploy_services:
	oc apply -f deploy/applications/rules_app.yaml -n ${PROD_NAMESPACE}
	oc apply -f deploy/applications/fraud_app.yaml -n ${PROD_NAMESPACE}
	oc apply -f deploy/services/archive_svc.yaml -n ${PROD_NAMESPACE}
	oc apply -f deploy/services/archive_fraud_svc.yaml -n ${PROD_NAMESPACE}
	oc apply -f deploy/services/archive_inbox_svc.yaml -n ${PROD_NAMESPACE}
	oc apply -f deploy/services/case_svc.yaml -n ${PROD_NAMESPACE}
	oc apply -f deploy/services/fraud_svc.yaml -n ${PROD_NAMESPACE}

.PHONY: deploy_demo_services
deploy_demo_services:
	oc apply -f deploy/demo/bridge_svc.yaml -n ${PROD_NAMESPACE}
	oc apply -f deploy/demo/bridge_fraud_svc.yaml -n ${PROD_NAMESPACE}
	
# basics to prepare the environment and the build tasks

.PHONY: config_infra
config_infra:
	oc apply -f deploy/limit-ranges.yaml -n ${PROD_NAMESPACE}
	oc policy add-role-to-user system:image-puller system:serviceaccount:${PROD_NAMESPACE}:default -n ${BUILD_NAMESPACE}
	oc policy add-role-to-user system:image-puller system:serviceaccount:${PROD_NAMESPACE}:default -n ${DEV_NAMESPACE}
	oc policy add-role-to-user system:image-puller system:serviceaccount:${DEV_NAMESPACE}:default -n ${BUILD_NAMESPACE}
	oc adm policy add-role-to-user admin system:serviceaccount:fsi-fraud-detection-xops:pipeline -n ${PROD_NAMESPACE}
	oc apply -f deploy/pvc_data.yaml -n ${PROD_NAMESPACE}
	oc apply -f deploy/pvc_models.yaml -n ${BUILD_NAMESPACE}

.PHONY: apply_config
apply_config:
	oc apply -f deploy/config_fsi_fraud_detection.yaml -n ${BUILD_NAMESPACE}
	oc apply -f deploy/config_fsi_fraud_detection.yaml -n ${PROD_NAMESPACE}
	oc apply -f secrets/build_secrets.yaml -n ${BUILD_NAMESPACE}
	oc apply -f secrets/deploy_secrets.yaml -n ${PROD_NAMESPACE}
	oc apply -f secrets/aws_secrets.yaml -n ${BUILD_NAMESPACE}
	oc apply -f secrets/aws_secrets.yaml -n ${PROD_NAMESPACE}

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
	oc import-image ubi8/s2i-base:1-343 --from=registry.access.redhat.com/ubi8/s2i-base:1-343 --confirm -n ${BUILD_NAMESPACE}
	oc import-image ubi8/s2i-base:latest --from=registry.access.redhat.com/ubi8/s2i-base:1-343 --confirm -n ${BUILD_NAMESPACE}
	oc import-image ubi8/python-39:1-51 --from=registry.access.redhat.com/ubi8/python-39:1-51 --confirm -n ${BUILD_NAMESPACE}
	oc import-image ubi8/python-39:latest --from=registry.access.redhat.com/ubi8/python-39:1-51 --confirm -n ${BUILD_NAMESPACE}
	oc apply -f builder/golang_custom/build_golang_base.yaml -n ${BUILD_NAMESPACE}

.PHONY: prepare_jupyter_lab
prepare_jupyter_lab:
	oc policy add-role-to-user system:image-builder \
		system:serviceaccount:${BUILD_NAMESPACE}:builder \
		--namespace=openshift
	oc apply -f builder/jupyter_lab/image_streams.yaml -n openshift
	oc apply -f builder/jupyter_lab/build_jupyter_lab.yaml -n ${BUILD_NAMESPACE}
	oc apply -f deploy/jupyter_lab.yaml -n ${DEV_NAMESPACE}

# cleanup tasks

.PHONY: cleanup
cleanup:
	oc delete build --all -n ${BUILD_NAMESPACE}
	oc delete pipelineruns,taskruns --all -n ${BUILD_NAMESPACE}
	oc delete pod --field-selector=status.phase==Succeeded -n ${BUILD_NAMESPACE}
	oc delete pod --field-selector=status.phase==Succeeded -n ${PROD_NAMESPACE}

.PHONY: undeploy_all
undeploy_all: cleanup
	oc delete routes,dc,pvc,services,configmaps,secrets -l app-owner=fsi-fraud-detection -n ${PROD_NAMESPACE}
	oc delete bc,is,configmaps,secrets,pvc -l app-owner=fsi-fraud-detection -n ${BUILD_NAMESPACE}
	oc delete is --all -n ${BUILD_NAMESPACE}

# devops tasks

.PHONY: build_all
build_all:
	oc start-build golang-base -n ${BUILD_NAMESPACE}
	oc start-build bridge-svc -n ${BUILD_NAMESPACE}
	oc start-build rules-app -n ${BUILD_NAMESPACE}
	oc start-build fraud-app -n ${BUILD_NAMESPACE}

.PHONY: rollout_all
rollout_all: rollout_apps rollout_svc rollout_demo_svc

.PHONY: rollout_svc
rollout_svc:
	oc rollout latest dc/router-svc -n ${PROD_NAMESPACE}
	oc rollout latest dc/case-svc -n ${PROD_NAMESPACE}
	oc rollout latest dc/audit-svc -n ${PROD_NAMESPACE}
	oc rollout latest dc/audit-inbox-svc -n ${PROD_NAMESPACE}
	oc rollout latest dc/audit-fraud-svc -n ${PROD_NAMESPACE}

.PHONY: rollout_apps
rollout_apps:
	oc rollout latest dc/fraud-app -n ${PROD_NAMESPACE}
	oc rollout latest dc/rules-app -n ${PROD_NAMESPACE}

.PHONY: rollout_demo_svc
rollout_demo_svc:
	oc rollout latest dc/bridge-svc -n ${PROD_NAMESPACE}
	oc rollout latest dc/bridge-fraud-svc -n ${PROD_NAMESPACE}