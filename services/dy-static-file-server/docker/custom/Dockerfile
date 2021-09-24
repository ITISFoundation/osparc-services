# TODO: Please set your custom image here and adapt the Dockerfile/entrypoint.sh accordingly
FROM joseluisq/static-web-server:2.0.2-alpine as production 
#
#  USAGE:
#     cd services/dy-static-file-server
#     docker build -f docker/custom/Dockerfile -t dy-static-file-server:prod  .
#     docker run dy-static-file-server:prod
#

ARG PYTHON_VERSION="3.8.10-r0"
ARG WORKDIR="/workdir"

ENV SC_BUILD_TARGET=production
ENV SERVER_ROOT="/www"
ENV INPUT_FOLDER="${SERVER_ROOT}/inputs"
ENV OUTPUT_FOLDER="${SERVER_ROOT}/outputs"
ENV SC_USER_ID=101
ENV SERVER_PORT=8080
ENV SERVER_LOG_LEVEL=debug

# creating own project's user
ENV SC_USER_ID 9004
ENV SC_USER_NAME scudy
RUN adduser -D -u ${SC_USER_ID} -s /bin/sh -h /home/${SC_USER_NAME} ${SC_USER_NAME}


LABEL maintainer=GitHK

RUN apk add --update --no-cache \
    "python3=${PYTHON_VERSION}" \
    py3-pip \
    su-exec
RUN pip3 install --upgrade \
    pip \
    virtualenv

RUN mkdir -p /venv
RUN python3 -m venv /venv

# add additional directories
RUN mkdir -p ${WORKDIR} && chown ${SC_USER_NAME}:${SC_USER_NAME} ${WORKDIR} && \
    mkdir -p /docker && chown ${SC_USER_NAME}:${SC_USER_NAME} /docker

COPY --chown=${SC_USER_NAME}:${SC_USER_NAME} docker/custom/*.sh /docker

# add python app requirements
COPY requirements/base.txt /tmp/requirements.txt
RUN /venv/bin/pip3 install -r /tmp/requirements.txt

COPY --chown=${SC_USER_NAME}:${SC_USER_NAME} static-content/hello-world.txt /www/hello-world.txt
COPY --chown=${SC_USER_NAME}:${SC_USER_NAME} src/dy_static_file_server ${WORKDIR}/dy_static_file_server


WORKDIR ${WORKDIR}/dy_static_file_server

EXPOSE 8080
ENTRYPOINT ["/bin/sh", "/docker/entrypoint.sh"]
CMD ["/docker/boot.sh"]