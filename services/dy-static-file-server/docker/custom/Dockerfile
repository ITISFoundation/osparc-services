# TODO: Please set your custom image here and adapt the Dockerfile/entrypoint.sh accordingly
FROM nginx:1.21.0-alpine as production 
#
#  USAGE:
#     cd services/dy-static-file-server
#     docker build -f docker/custom/Dockerfile -t dy-static-file-server:prod  .
#     docker run dy-static-file-server:prod
#

# making nginx user simialar => # simcore-user uid=8004(scu) gid=8004(scu) groups=8004(scu)
# shadow required for groupmod and usermod
RUN apk --no-cache add shadow && \
    groupmod -g 8004 nginx && \
    usermod -u 8004 -g 8004 nginx

ARG PYTHON_VERSION="3.8.10-r0"
ARG INPUT_DIR="/www/inputs"
ARG OUTPUT_DIR="/www/outputs"
ARG WORKDIR="/workdir"
ARG USER="nginx"

LABEL maintainer=GitHK
COPY docker/custom/nginx.conf /etc/nginx/nginx.conf
COPY docker/custom/default.conf /etc/nginx/conf.d/default.conf
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


RUN mkdir -p ${INPUT_DIR} && \
    mkdir -p ${OUTPUT_DIR} && \
    mkdir -p ${WORKDIR}

COPY static-content/hello-world.txt /www/hello-world.txt
COPY src/dy_static_file_server ${WORKDIR}/dy_static_file_server

## add permissions
RUN chown -R ${USER}:${USER} /boot.sh && \
    chown -R ${USER}:${USER} /var/cache/nginx && \
    chown -R ${USER}:${USER} /var/log/nginx && \
    chown -R ${USER}:${USER} /etc/nginx/conf.d && \
    chown -R ${USER}:${USER} /etc/nginx/conf.d/default.conf && \
    chown -R ${USER}:${USER} ${INPUT_DIR} && \
    chown -R ${USER}:${USER} ${OUTPUT_DIR} && \
    chown -R ${USER}:${USER} ${WORKDIR}

RUN touch /var/run/nginx.pid && \
    chown -R ${USER}:${USER} /var/run/nginx.pid

## switch to non-root user
USER ${USER}

ENV NGINX_SERVER_ROOT="/www"

WORKDIR ${WORKDIR}/dy_static_file_server

EXPOSE 8080
CMD [ "/bin/sh", "/boot.sh" ]