FROM node:8.15.0-alpine as base

LABEL maintainer=odeimaiz

# non-root user 'scu'
RUN adduser -D -u 8004 scu

RUN apk add --no-cache \
    su-exec

ENV HOME /home/scu

EXPOSE 4000

WORKDIR $HOME

RUN apk update &&\
    apk add --no-cache \
    python3 \
    bash


RUN pip3 install --upgrade pip wheel setuptools

# ----------------------------------------------------------------
# install simcore-sdk
RUN apk add --no-cache --virtual .build-deps \
    g++ \
    git \
    python3-dev \
    postgresql-dev && \
    pip install --no-cache-dir git+https://github.com/ITISFoundation/osparc-simcore.git@master#subdirectory=packages/simcore-sdk &&\
    pip install --no-cache-dir git+https://github.com/ITISFoundation/osparc-simcore.git@master#subdirectory=services/storage/client-sdk/python &&\
    pip install --no-cache-dir git+https://github.com/ITISFoundation/osparc-simcore.git@master#subdirectory=packages/postgres-database &&\
    apk del --no-cache .build-deps


RUN npm install express

# ----------------------------------------------------------------
# set up oSparc env variables
ENV SIMCORE_NODE_UUID="-1" \
    SIMCORE_USER_ID="-1" \
    SIMCORE_NODE_BASEPATH="/tissue-properties" \
    STORAGE_ENDPOINT="=1" \
    S3_ENDPOINT="=1" \
    S3_ACCESS_KEY="-1" \
    S3_SECRET_KEY="-1" \
    S3_BUCKET_NAME="-1" \
    POSTGRES_ENDPOINT="-1" \
    POSTGRES_USER="-1" \
    POSTGRES_PASSWORD="-1" \
    POSTGRES_DB="-1"

#-----------------Production----------------------
FROM base AS production

COPY --chown=scu:scu services/dy-tissue-properties/csv-to-html-table $HOME/csv-to-html-table
COPY --chown=scu:scu services/dy-tissue-properties/inputs/TissueProperties.csv $HOME/csv-to-html-table/data/TissueProperties.csv

RUN apk add --no-cache \
  postgresql-libs

# --------------- Healthcheck -------------------
COPY --chown=scu:scu scripts/docker/healthcheck.py $HOME/healthcheck/healthcheck.py
# will start to run after interval every interval. fails after timeout. fail do not count if during start-period. will do # retries
HEALTHCHECK --interval=10s --timeout=30s --start-period=1s --retries=3 CMD [ "python3", "/home/scu/healthcheck/healthcheck.py", "http://localhost:4000" ]

WORKDIR $HOME
COPY --chown=scu:scu services/dy-tissue-properties/docker $HOME/docker
COPY --chown=scu:scu services/dy-tissue-properties/server $HOME/server

WORKDIR $HOME/csv-to-html-table
CMD ["/bin/bash", "../docker/boot.sh"]

#-----------------Development-----------------------
FROM base as development

VOLUME $HOME/scripts
VOLUME $HOME/services/storage/client-sdk

VOLUME $HOME/csv-to-html-table
VOLUME $HOME/docker
VOLUME $HOME/server
VOLUME $HOME/devel

COPY --chown=scu /scripts/dy_services_helpers/requirements.txt $HOME/scripts/dy_services_helpers/requirements.txt
RUN pip3 install -r $HOME/scripts/dy_services_helpers/requirements.txt

ENV CREATE_DUMMY_TABLE 1
ENV USE_CASE_CONFIG_FILE="/home/scu/devel/port_config.json"
ENV INIT_OPTIONS="50 6 1 tab"

WORKDIR $HOME/csv-to-html-table
ENTRYPOINT ["/bin/bash", "../docker/boot.sh"]
