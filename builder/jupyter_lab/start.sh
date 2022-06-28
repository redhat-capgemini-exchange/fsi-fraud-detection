#!/bin/bash
set -e

# set default ip to 0.0.0.0
if [[ "${NOTEBOOK_ARGS} $*" != *"--ip="* ]]; then
    NOTEBOOK_ARGS="--ip=0.0.0.0 ${NOTEBOOK_ARGS}"
fi

# set default to $DATA_ROOT
if [[ "${NOTEBOOK_ARGS} $*" != *"--notebook-dir="* ]]; then
    NOTEBOOK_ARGS="--notebook-dir=${NOTEBOOK_ROOT} ${NOTEBOOK_ARGS}"
fi

echo " --> jupyter ${JUPYTER_CMD} ${NOTEBOOK_ARGS}"

exec jupyter ${JUPYTER_CMD} ${NOTEBOOK_ARGS} "$@"