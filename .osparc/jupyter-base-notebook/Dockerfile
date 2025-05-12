ARG BASE_IMAGE=jupyter/base-notebook:notebook-6.2.0
FROM ${BASE_IMAGE} AS base

LABEL maintainer="sanderegg"
EXPOSE 8888

USER root
ENV NB_UID=8004
ENV NB_GID=100
RUN usermod  -u $NB_UID $NB_USER
RUN apt-get update &&\
    apt-get install -y \
    git \
    gcc
USER $NB_USER
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
# specific notebook env
ENV NOTEBOOK_TOKEN="simcore"
# ----------------------------------------------------------------
COPY --chown=1000:100 scripts/docker/healthcheck_curl_host.py /healthcheck/healthcheck_curl_host.py
# will start to run after interval every interval. fails after timeout. fail do not count if during start-period. will do # retries
HEALTHCHECK --interval=10s --timeout=30s --start-period=1s --retries=3 CMD [ "python3", "/healthcheck/healthcheck_curl_host.py", "http://localhost:8888" ]
# configure notebook
RUN pip install --upgrade pip && \
    pip install jupyter_contrib_nbextensions && \
    pip install jupyterthemes && \
    jt -t oceans16 -T -N -kl && \
    jupyter contrib nbextensions install --user && \
    jupyter nbextension enable hide_input/main && \
    jupyter nbextension enable init_cell/main
# ----------------------------------------------------------------
ENV PYTHONPATH=/home/jovyan/handlers
# ----------------------------------------------------------------


RUN pip install --no-cache-dir markupsafe==2.0.1

ENV INPUTS_FOLDER=/home/jovyan/inputs
ENV OUTPUTS_FOLDER=/home/jovyan/outputs

# ----------------------------------------------------------------
FROM base AS development
VOLUME /home/jovyan/packages
VOLUME /home/jovyan/services
VOLUME /home/jovyan/devel
VOLUME /home/root/scripts/dy_services_helpers
VOLUME /home/jovyan/docker
VOLUME /home/jovyan/handlers
# increase development speed by pre-installing libraries
COPY --chown=1000:100 services/jupyter-base-notebook/devel/requirements.txt /home/jovyan/devel/requirements.txt
RUN pip install -r /home/jovyan/devel/requirements.txt
ENV CREATE_DUMMY_TABLE=1
ENV USE_CASE_CONFIG_FILE="devel/port_config.json"
ENV TEST_DATA_PATH="/test-data"

CMD [ "/bin/bash", "/docker/boot.sh" ]

# ----------------------------------------------------------------
FROM base AS production
# prepare for booting
COPY --chown=1000:100 services/jupyter-base-notebook/docker /docker
# install simcore packages. docker seems to set root:root permission to the implicitely created destination folders
COPY --chown=1000:100 services/jupyter-base-notebook/handlers/* /home/jovyan/handlers/
# copy the default notebook
COPY --chown=1000:100 services/jupyter-base-notebook/notebooks /home/jovyan/notebooks
USER root
RUN mkdir -p /home/jovyan/inputs && mkdir -p /home/jovyan/outputs 
RUN chmod -R 777 /home/jovyan/notebooks && chmod -R 777 /home/jovyan/inputs && chmod -R 777 /home/jovyan/outputs
USER $NB_USER
# cleanup
RUN rm -rf /home/jovyan/packages && \
    rm -rf /home/jovyan/services

ENTRYPOINT [ "/bin/bash", "/docker/boot.sh" ]
