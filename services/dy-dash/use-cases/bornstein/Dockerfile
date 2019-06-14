#ARG BASE_IMAGE
FROM itisfoundation/jupyter-neuron:latest AS common
LABEL maintainer="maiz"

# install requirements --------------------------------------------------------
COPY --chown=jovyan:users mattward/requirements.txt .
# TODO: tmp workaround for https://github.com/pypa/pip/issues/6197
RUN pip --cache-dir=/tmp/.pipcache install -r requirements.txt &&\
    rm -rf /tmp/.pipcache


# prepare for booting ---------------------------------------------------------
COPY --chown=jovyan:users docker /docker
# set of arguments to copy the right app ---------------------------------
ARG APP_NAME
ENV APP_URL=${APP_NAME}

EXPOSE 8888
# -----------------------------------------------------------------------------
FROM common AS development
VOLUME /home/jovyan/services
VOLUME /home/jovyan/devel
VOLUME /home/jovyan/devel-config
VOLUME /home/jovyan/app
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
# set of arguments to copy the right app
ARG APP_NAME
# copy the app in the image
WORKDIR /home/jovyan/app
COPY --chown=jovyan:users mattward/app/${APP_NAME} ${APP_NAME}
ENTRYPOINT [ "/bin/bash", "/docker/boot.sh" ]
