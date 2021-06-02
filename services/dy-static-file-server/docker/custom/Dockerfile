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
COPY docker/custom/hello-world.txt /www/hello-world.txt
COPY docker/custom/boot.sh /boot.sh

ENV NGINX_SERVER_ROOT="/www"

FROM base as production

# # set up oSparc env variables
# ENV SIMCORE_NODE_UUID="-1" \
#     SIMCORE_USER_ID="-1" \
#     SIMCORE_NODE_BASEPATH="" \
#     SIMCORE_NODE_APP_STATE_PATH="/www" \
#     STORAGE_ENDPOINT="=1" \
#     S3_ENDPOINT="=1" \
#     S3_ACCESS_KEY="-1" \
#     S3_SECRET_KEY="-1" \
#     S3_BUCKET_NAME="-1" \
#     POSTGRES_ENDPOINT="-1" \
#     POSTGRES_USER="-1" \
#     POSTGRES_PASSWORD="-1" \
#     POSTGRES_DB="-1"

CMD [ "/bin/sh", "/boot.sh" ]