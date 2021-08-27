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

COPY src/dy_static_file_server/hello-world.txt /www/hello-world.txt
RUN mkdir -p /www/inputs-outputs

ENV NGINX_SERVER_ROOT="/www"

FROM base as production

CMD [ "/bin/sh", "/boot.sh" ]