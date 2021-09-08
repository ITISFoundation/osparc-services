# TODO: Please set your custom image here and adapt the Dockerfile/entrypoint.sh accordingly
FROM nginx:1.21.0-alpine as base 
#
#  USAGE:
#     cd services/dy-static-file-server
#     docker build -f Dockerfile -t dy-static-file-server:prod --target production ../../
#     docker run dy-static-file-server:prod
#

LABEL maintainer=sanderegg
COPY docker/custom/nginx.conf /etc/nginx/nginx.conf
COPY docker/custom/boot.sh /boot.sh

RUN apk add --update --no-cache "python3=3.8.10-r0" py3-pip
RUN pip3 install --upgrade pip

# add python app requirements
COPY requirements_app.txt /tmp/requirements_app.txt
RUN python3 --version
RUN pip list
RUN pip3 install -r /tmp/requirements_app.txt

COPY static-content/hello-world.txt /www/hello-world.txt
RUN mkdir -p /www/inputs
RUN mkdir -p /www/outputs

RUN mkdir -p /workdir
COPY src/dy_static_file_server /workdir/dy_static_file_server

ENV NGINX_SERVER_ROOT="/www"

FROM base as production

WORKDIR /workdir/dy_static_file_server

CMD [ "/bin/sh", "/boot.sh" ]