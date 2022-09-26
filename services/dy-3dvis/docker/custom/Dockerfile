# this must be the first line
ARG BASE_IMAGE=kitware/paraviewweb:pv-v5.6.0-osmesa
# apply patch to visualizer
FROM node:8.12.0 AS visualizer
WORKDIR /home/node
ARG VISUALIZER_VERSION=v3.1.10
RUN git clone --branch ${VISUALIZER_VERSION} https://github.com/Kitware/visualizer.git
WORKDIR /home/node/visualizer
COPY services/dy-3dvis/src/3d-viewer/rebrand-osparc/to-be-copied .
COPY services/dy-3dvis/src/3d-viewer/rebrand-osparc/rebrand-osparc.patch rebrand-osparc.patch
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
# git checkout `git rev-list -1 --before="2021-03-22T16:24:04Z" master`

RUN export PATH="${PYENV_ROOT}/bin:$PATH" && \
    eval "$(pyenv init -)" && \
    pip install git+git://github.com/ITISFoundation/osparc-simcore.git@aa717c7c83a789738dfa37bf52b29e400a5d8e90#subdirectory=packages/service-library \
    git+git://github.com/ITISFoundation/osparc-simcore.git@aa717c7c83a789738dfa37bf52b29e400a5d8e90#subdirectory=packages/models-library \
    git+git://github.com/ITISFoundation/osparc-simcore.git@aa717c7c83a789738dfa37bf52b29e400a5d8e90#subdirectory=packages/simcore-sdk \
    git+git://github.com/ITISFoundation/osparc-simcore.git@aa717c7c83a789738dfa37bf52b29e400a5d8e90#subdirectory=services/storage/client-sdk/python \
    git+git://github.com/ITISFoundation/osparc-simcore.git@aa717c7c83a789738dfa37bf52b29e400a5d8e90#subdirectory=packages/postgres-database


# get the patched visualizer
COPY --from=visualizer /home/node/visualizer/dist /opt/paraview/share/paraview-5.6/web/visualizer/www
WORKDIR /home/root
# ----------------------------------------------------------------
# set up oSparc env variables
ENV SIMCORE_NODE_UUID="-1" \
    SIMCORE_USER_ID="-1" \
    SIMCORE_NODE_BASEPATH="" \
    SIMCORE_NODE_APP_STATE_PATH=${PARAVIEW_INPUT_PATH} \
    SIMCORE_HOST_NAME="localhost" \
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
ENV SERVER_PORT="80"  \
    SIMCORE_STATE_FILE="simcore-state.pvsm" \
    PARAVIEW_DEBUG=0

RUN mkdir /home/root/trigger && \
    chmod 777 /home/root/trigger


#------------------------------------------
FROM common AS production
# will start to run after interval every interval. fails after timeout. fail do not count if during start-period. will do # retries
HEALTHCHECK --interval=10s --timeout=30s --start-period=1s --retries=3 CMD [ "python3", "/home/root/docker/healthcheck_curl_host.py", "http://localhost", "/" ]
# copy scripts
COPY services/dy-3dvis/docker/custom /home/root/docker
COPY services/dy-3dvis/src/3d-viewer/utils /home/root/utils
COPY services/dy-3dvis/src/3d-viewer/config /home/root/config
COPY services/dy-3dvis/src/3d-viewer/handlers/*.rpy /opt/paraview/share/paraview-5.6/web/visualizer/www/

ENTRYPOINT [ "/bin/bash", "docker/entrypoint.bash" ]
#------------------------------------------
FROM common as development
ENV CREATE_DUMMY_TABLE 1
ENV USE_CASE_CONFIG_FILE="devel/port_config.json"
ENV TEST_DATA_PATH="/test-data"
# Need to use entrypoint as base image's entrypoint must be overriden
ENTRYPOINT [ "/bin/bash", "docker/entrypoint.bash" ]

