# this must be the first line
ARG BASE_IMAGE=kitware/paraviewweb:pv-v5.6.0-osmesa
# apply patch to visualizer
FROM node:8.12.0 AS visualizer
WORKDIR /home/node
ARG VISUALIZER_VERSION=v3.1.10
RUN git clone --branch ${VISUALIZER_VERSION} https://github.com/Kitware/visualizer.git
WORKDIR /home/node/visualizer
COPY services/dy-3dvis/simcoreparaviewweb/rebrand-osparc/to-be-copied .
COPY services/dy-3dvis/simcoreparaviewweb/rebrand-osparc/rebrand-osparc.patch rebrand-osparc.patch
RUN git apply rebrand-osparc.patch && \
    npm install && \
    npm run build:release && \
    npm link && \
    cp src/*.png dist
# ----------------------------------------------------------------
# build visualizer service
FROM ${BASE_IMAGE}  AS common

LABEL maintainer="sanderegg"
ENV PARAVIEW_INPUT_PATH="/data"

USER root
# install git, pip
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3-pip &&\
    rm -rf /var/lib/apt/lists/*

# install python 3.6 for root and also for www-data
ENV PYENV_ROOT=/pyenv
# necessary to prevent some dependencies to ask questions while installing
ENV DEBIAN_FRONTEND=noninteractive
RUN curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash && \
    export PATH="${PYENV_ROOT}/bin:$PATH" && \
    eval "$(pyenv init -)" && \
    eval "$(pyenv virtualenv-init -)" && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    make build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
    xz-utils tk-dev libffi-dev liblzma-dev && \
    pyenv install 3.6.7 && \
    pyenv global 3.6.7 && \
    pip install --upgrade pip wheel setuptools &&\
    apt-get remove -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
    xz-utils tk-dev libffi-dev liblzma-dev &&\
    apt-get autoremove -y &&\
    apt-get clean -y &&\
    rm -rf /var/lib/apt/lists/*

# ----------------------------------------------------------------
# install simcore-sdk
RUN export PATH="${PYENV_ROOT}/bin:$PATH" && \
    eval "$(pyenv init -)" && \
    pip install git+https://github.com/ITISFoundation/osparc-simcore.git@master#subdirectory=packages/simcore-sdk &&\
    pip install git+https://github.com/ITISFoundation/osparc-simcore.git@master#subdirectory=services/storage/client-sdk/python

# get the patched visualizer
COPY --from=visualizer /home/node/visualizer/dist /opt/paraview/share/paraview-5.6/web/visualizer/www
WORKDIR /home/root
# ----------------------------------------------------------------
COPY scripts/docker/healthcheck_curl_host.py /healthcheck/healthcheck_curl_host.py
# will start to run after interval every interval. fails after timeout. fail do not count if during start-period. will do # retries
#HEALTHCHECK --interval=10s --timeout=30s --start-period=1s --retries=3 CMD [ "python3", "/healthcheck/healthcheck_curl_host.py", "http://localhost:80/visualizer" ]

# set up oSparc env variables
ENV SIMCORE_NODE_UUID="-1" \
    SIMCORE_USER_ID="-1" \
    SIMCORE_NODE_BASEPATH="" \
    SIMCORE_NODE_APP_STATE_PATH="/data" \
    STORAGE_ENDPOINT="=1" \
    S3_ENDPOINT="=1" \
    S3_ACCESS_KEY="-1" \
    S3_SECRET_KEY="-1" \
    S3_BUCKET_NAME="-1" \
    POSTGRES_ENDPOINT="-1" \
    POSTGRES_USER="-1" \
    POSTGRES_PASSWORD="-1" \
    POSTGRES_DB="-1"

# special paraview variables
ENV SERVER_PORT="-1"  \
    HOST_NAME="-1"

RUN mkdir /home/root/trigger && \
    chmod 777 /home/root/trigger
#------------------------------------------
FROM common AS production
# copy scripts
COPY services/dy-3dvis/simcoreparaviewweb/docker /home/root/docker
COPY services/dy-3dvis/simcoreparaviewweb/config /home/root/config
COPY services/dy-3dvis/simcoreparaviewweb/handlers/*.rpy /opt/paraview/share/paraview-5.6/web/visualizer/www/
ENTRYPOINT [ "/bin/bash", "docker/boot.sh" ]
#------------------------------------------
FROM common as development
VOLUME /home/root/devel
VOLUME /home/root/services
VOLUME /home/root/test-data
VOLUME /home/root/scripts/dy_services_helpers
VOLUME /home/root/docker
VOLUME /home/root/config
ENV CREATE_DUMMY_TABLE 1
ENV USE_CASE_CONFIG_FILE="devel/port_config.json"
ENV TEST_DATA_PATH="/test-data"
# Need to use entrypoint as base image's entrypoint must be overriden
ENTRYPOINT [ "/bin/bash", "docker/boot.sh" ]

