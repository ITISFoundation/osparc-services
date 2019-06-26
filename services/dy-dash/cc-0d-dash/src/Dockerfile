#ARG BASE_IMAGE
FROM itisfoundation/cnap-dy-jupyter:latest AS common
LABEL maintainer=odeimaiz

# install requirements --------------------------------------------------------
COPY --chown=jovyan:users src/requirements.txt .
# TODO: tmp workaround for https://github.com/pypa/pip/issues/6197
RUN pip --cache-dir=/tmp/.pipcache install -r requirements.txt &&\
    rm -rf /tmp/.pipcache


# prepare for booting ---------------------------------------------------------
COPY --chown=jovyan:users docker /docker
# set of arguments to copy the right app ---------------------------------
ARG APP_NAME
ENV APP_URL=${APP_NAME}

EXPOSE 8888
# ----------------------------------------------------------------
# set up oSparc env variables
ENV SIMCORE_NODE_UUID="-1" \
    SIMCORE_USER_ID="-1" \
    SIMCORE_NODE_BASEPATH="" \
    SIMCORE_NODE_APP_STATE_PATH="/home/jovyan/notebooks" \
    STORAGE_ENDPOINT="=1" \
    S3_ENDPOINT="=1" \
    S3_ACCESS_KEY="-1" \
    S3_SECRET_KEY="-1" \
    S3_BUCKET_NAME="-1" \
    POSTGRES_ENDPOINT="-1" \
    POSTGRES_USER="-1" \
    POSTGRES_PASSWORD="-1" \
    POSTGRES_DB="-1"
# ----------------------------------------------------------------
COPY --chown=jovyan:users /docker/scripts/healthcheck_curl_host.py /healthcheck/healthcheck_curl_host.py
# will start to run after interval every interval. fails after timeout. fail do not count if during start-period. will do # retries
HEALTHCHECK --interval=10s --timeout=30s --start-period=1s --retries=3 CMD [ "python3", "/healthcheck/healthcheck_curl_host.py", "http://localhost:8888" ]
# -----------------------------------------------------------------------------
FROM common AS development
ENV SC_BUILD_TARGET=development
VOLUME /home/jovyan/services
VOLUME /home/jovyan/devel
VOLUME /home/jovyan/devel-config
VOLUME /home/jovyan/src
VOLUME /home/jovyan/input
VOLUME /home/jovyan/output
ENV USE_CASE_CONFIG_FILE="node_configuration_file.json"
ENV INIT_OPTIONS="100 6000 20 space"
ENV CREATE_DUMMY_TABLE=1
# switch off the default entrypoint
ENTRYPOINT []
CMD [ "/bin/bash", "/docker/boot.sh" ]
# -----------------------------------------------------------------------------
FROM common AS production
ENV SC_BUILD_TARGET=production
RUN mkdir -p /home/jovyan/output
# set of arguments to copy the right app
ARG APP_NAME
# copy the app in the image
WORKDIR /home/jovyan/src
# COPY --chown=jovyan:users src/cc-0d-dash/${APP_NAME} ${APP_NAME}
COPY --chown=jovyan:users src/cc-0d-dash .
ENTRYPOINT [ "/bin/bash", "/docker/boot.sh" ]
