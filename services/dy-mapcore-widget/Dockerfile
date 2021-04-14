FROM ubuntu:18.04 as base

LABEL maintainer=odeimaiz

# non-root user 'scu'
ENV SC_USER_ID 8004
ENV SC_USER_NAME scu
RUN adduser --uid ${SC_USER_ID} --disabled-password --gecos "" --shell /bin/sh --home /home/${SC_USER_NAME} ${SC_USER_NAME}

RUN apt -qq update && \
    apt install -y \
    jq \
    curl \
    python3-pip &&\
    rm -rf /var/lib/apt/lists/*

ENV HOME /home/scu

EXPOSE 4000

WORKDIR $HOME


RUN pip3 install --upgrade pip wheel setuptools

# ----------------------------------------------------------------
# install simcore-sdk
RUN apt-get update && apt-get install -y \
    g++ \
    git \
    python3-dev \
    postgresql-server-dev-10 && \
    pip install --no-cache-dir git+https://github.com/ITISFoundation/osparc-simcore.git@master#subdirectory=packages/service-library &&\
    pip install --no-cache-dir git+https://github.com/ITISFoundation/osparc-simcore.git@master#subdirectory=packages/simcore-sdk &&\
    pip install --no-cache-dir git+https://github.com/ITISFoundation/osparc-simcore.git@master#subdirectory=services/storage/client-sdk/python &&\
    pip install --no-cache-dir git+https://github.com/ITISFoundation/osparc-simcore.git@master#subdirectory=packages/postgres-database
RUN curl -sL https://deb.nodesource.com/setup_14.x |  bash -
RUN  apt -y install nodejs

# ----------------------------------------------------------------
# install service related resources
# - clone repo
# - checkout Alan Wu branch from his repo https://github.com/alan-wu/mapintegratedvuer/tree/13-Apr-Simcore
# - fix it to 638edaa37f8743300f1253fcd347b72a3a1e6a09 commit
# - we build in static mode (only mode that seem to work out of the box) and for this we need to disable the webpack analyzer that blocks in the docker building phase
# - replace the endpoint of the Mapcore API to access no-cors and actually access an existing endpoint
# - build/compile
# - replace the first slash from href="/ and src="/ in index.html to be able to access relative path


RUN git clone https://github.com/alan-wu/mapintegratedvuer.git mapintegratedvuer &&\
    cd mapintegratedvuer &&\
    git checkout 13-Apr-Simcore &&\
    git reset --hard 638edaa37f8743300f1253fcd347b72a3a1e6a09 &&\
    npm install --save &&\
    sed --in-place "s/openAnalyzer: false/openAnalyzer: false, analyzerMode: 'disabled'/" vue.config.js &&\
    sed --in-place --regexp-extended 's%VUE_APP_API_LOCATION=(.*)%VUE_APP_API_LOCATION=https://mapcore-demo.org/current/sparc-api-v2/%' .env &&\
    ./node_modules/.bin/vue-cli-service build --mode static &&\
    sed --in-place 's%href="/%href="%g' dist/index.html &&\
    sed --in-place 's%src="/%src="%g' dist/index.html


RUN npm install express

# ----------------------------------------------------------------
# set up oSparc env variables
ENV SIMCORE_NODE_UUID="-1" \
    SIMCORE_USER_ID="-1" \
    SIMCORE_NODE_BASEPATH="/mapcore-widget" \
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

COPY --from=base --chown=scu:scu $HOME/mapintegratedvuer $HOME/mapintegratedvuer

RUN apt install \
    libpq-dev

# --------------- Healthcheck -------------------
COPY --chown=scu:scu scripts/docker/healthcheck.py $HOME/healthcheck/healthcheck.py
# will start to run after interval every interval. fails after timeout. fail do not count if during start-period. will do # retries
HEALTHCHECK --interval=10s --timeout=30s --start-period=1s --retries=3 CMD [ "python3", "/home/scu/healthcheck/healthcheck.py", "http://localhost:4000" ]

WORKDIR $HOME
COPY --chown=scu:scu services/dy-mapcore-widget/docker $HOME/docker
COPY --chown=scu:scu services/dy-mapcore-widget/server $HOME/server

WORKDIR $HOME/mapintegratedvuer
CMD ["/bin/bash", "../docker/boot.sh"]

#-----------------Development-----------------------
FROM base as development

VOLUME $HOME/scripts
VOLUME $HOME/services/storage/client-sdk

VOLUME $HOME/mapintegratedvuer
VOLUME $HOME/docker
VOLUME $HOME/server
VOLUME $HOME/devel

ENV CREATE_DUMMY_TABLE 1
ENV USE_CASE_CONFIG_FILE="/home/scu/devel/port_config.json"
ENV INIT_OPTIONS="50 6 1 tab"

WORKDIR $HOME/mapintegratedvuer
ENTRYPOINT ["/bin/bash", "../docker/boot.sh"]
