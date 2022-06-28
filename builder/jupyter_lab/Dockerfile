FROM registry.access.redhat.com/ubi8/python-39:1-51

ENV APP_SCRIPT=/opt/app-root/bin/start.sh \
    DATA_ROOT=/opt/app-root/data \
    NOTEBOOK_ROOT=/opt/app-root/src \
    JUPYTER_LAB_VERSION=3.4.0 \
    JUPYTER_CMD=lab \
    JUPYTER_PORT=8080 \
    JUPYTER_DATA_DIR=/opt/app-root/data \
    JUPYTER_CONFIG_DIR=/opt/app-root/data/.jupyter

USER root

# create all folders first
RUN mkdir -p ${DATA_ROOT} && \
    chown -R 1001:0 ${DATA_ROOT} && \
    fix-permissions ${DATA_ROOT} -P

RUN mkdir -p ${NOTEBOOK_ROOT} && \
    chown -R 1001:0 ${NOTEBOOK_ROOT} && \
    fix-permissions ${NOTEBOOK_ROOT} -P

RUN mkdir -p ${JUPYTER_CONFIG_DIR} && \
    chown -R 1001:0 ${JUPYTER_CONFIG_DIR} && \
    fix-permissions ${JUPYTER_CONFIG_DIR} -P

# install JupyterLab and everything else
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

RUN jupyter ${JUPYTER_CMD} --generate-config && \
    npm cache clean --force && \
    jupyter lab clean

RUN chown -R 1001:0 ${APP_ROOT} && \
    fix-permissions ${APP_ROOT} -P && \
    rpm-file-permissions

# the default start script, can be changed by setting $APP_SCRIPT
COPY start.sh /opt/app-root/bin/start.sh
RUN chmod +x /opt/app-root/bin/start.sh && \
    chown default:root /opt/app-root/bin/start.sh

USER 1001

# Set the default CMD to run the notebook
CMD $APP_SCRIPT