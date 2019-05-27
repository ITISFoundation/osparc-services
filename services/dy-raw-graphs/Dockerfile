FROM node:8.15.0-alpine as base

LABEL maintainer=odeimaiz

# non-root user 'scu'
RUN adduser -D -u 8004 scu

RUN apk add --no-cache \
    su-exec

ENV HOME /home/scu

EXPOSE 4000

WORKDIR $HOME

RUN apk update && \
    apk add python3 && \
    apk add bash && \
    apk add git && \
    apk add postgresql-dev && \
    apk add py-pip

# TODO: Move the devel specific packages to develoment stage
RUN apk add --no-cache \
    gcc \
    subversion \
    g++ \
    libc-dev \
    libffi-dev \
    python3-dev

RUN pip3 install --upgrade pip wheel setuptools

# ----------------------------------------------------------------
# install simcore-sdk
RUN pip install git+https://github.com/ITISFoundation/osparc-simcore.git@master#subdirectory=packages/simcore-sdk &&\
    pip install git+https://github.com/ITISFoundation/osparc-simcore.git@master#subdirectory=services/storage/client-sdk/python

RUN npm install express

# ----------------------------------------------------------------
# set up oSparc env variables
ENV SIMCORE_NODE_UUID="-1" \
    SIMCORE_USER_ID="-1" \
    SIMCORE_NODE_BASEPATH="/raw" \
    STORAGE_ENDPOINT="=1" \
    RAWGRAPHS_INPUT_PATH="../inputs" \
    RAWGRAPHS_OUTPUT_PATH="../outputs" \
    S3_ENDPOINT="=1" \
    S3_ACCESS_KEY="-1" \
    S3_SECRET_KEY="-1" \
    S3_BUCKET_NAME="-1" \
    POSTGRES_ENDPOINT="-1" \
    POSTGRES_USER="-1" \
    POSTGRES_PASSWORD="-1" \
    POSTGRES_DB="-1"

#-----------------Development-----------------------
FROM base as development

VOLUME $HOME/scripts
VOLUME $HOME/services/storage/client-sdk

VOLUME $HOME/raw
VOLUME $HOME/docker
VOLUME $HOME/inputs
VOLUME $HOME/server
VOLUME $HOME/devel

COPY --chown=scu /scripts/dy_services_helpers/requirements.txt $HOME/scripts/dy_services_helpers/requirements.txt
RUN pip3 install -r $HOME/scripts/dy_services_helpers/requirements.txt

ENV CREATE_DUMMY_TABLE 1
ENV USE_CASE_CONFIG_FILE="/home/scu/devel/port_config.json"
ENV INIT_OPTIONS="50 6 1 tab"

WORKDIR $HOME/raw
ENTRYPOINT ["/bin/bash", "../docker/boot.sh"]

#-----------------Production----------------------
FROM base AS production

ARG BRANCH_NAME
RUN git clone https://github.com/ITISFoundation/raw.git --branch ${BRANCH_NAME}
WORKDIR $HOME/raw
RUN npm install -g bower
RUN bower install --force --allow-root

WORKDIR $HOME
COPY --chown=scu:scu services/dy-raw-graphs/docker $HOME/docker
COPY --chown=scu:scu services/dy-raw-graphs/server $HOME/server

WORKDIR $HOME/raw
CMD ["/bin/bash", "../docker/boot.sh"]
