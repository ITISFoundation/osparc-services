# TODO: Please set your custom image here and adapt the Dockerfile/entrypoint.sh accordingly
FROM nginx:1.21.0-alpine as production 
#
#  USAGE:
#     cd services/dy-static-file-server
#     docker build -f docker/custom/Dockerfile -t dy-static-file-server:prod  .
#     docker run dy-static-file-server:prod
#

ARG PYTHON_VERSION="3.8.10-r0"
ARG INPUT_DIR="/www/inputs"
ARG OUTPUT_DIR="/www/outputs"
ARG WORKDIR="/workdir"

LABEL maintainer=GitHK
COPY docker/custom/nginx.conf /etc/nginx/nginx.conf
COPY docker/custom/boot.sh /boot.sh

RUN apk add --update --no-cache \
    "python3=${PYTHON_VERSION}" \
    py3-pip
RUN pip3 install --upgrade \
    pip \
    virtualenv

RUN mkdir -p /venv
RUN python3 -m venv /venv

# add python app requirements
COPY requirements/base.txt /tmp/requirements.txt
RUN /venv/bin/pip3 install -r /tmp/requirements.txt

COPY static-content/hello-world.txt /www/hello-world.txt

RUN mkdir -p ${INPUT_DIR} && \
    mkdir -p ${OUTPUT_DIR} && \
    mkdir -p ${WORKDIR}

COPY src/dy_static_file_server ${WORKDIR}/dy_static_file_server

ENV NGINX_SERVER_ROOT="/www"

WORKDIR ${WORKDIR}/dy_static_file_server

CMD [ "/bin/sh", "/boot.sh" ]