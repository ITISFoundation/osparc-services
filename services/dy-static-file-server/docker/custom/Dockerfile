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

# RUN apt-get update &&  \
#     apt-get install -y software-properties-common && \
#     add-apt-repository ppa:deadsnakes/ppa \
#     apt-get install -y python3-9 && \
#     apt-get install -y python3-pip 

RUN python3 --version

# add python app requirements
COPY requirements_app.txt /tmp/requirements_app.txt
RUN pip3 install -r /tmp/requirements_app.txt

COPY static-content/hello-world.txt /www/hello-world.txt
RUN mkdir -p /www/inputs
RUN mkdir -p /www/outputs

ENV NGINX_SERVER_ROOT="/www"

FROM base as production

CMD [ "/bin/sh", "/boot.sh" ]