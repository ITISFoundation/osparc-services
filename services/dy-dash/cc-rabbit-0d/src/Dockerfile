FROM alpine:3.7 as base
#
#  USAGE:
#     cd services/cc-rabbit-0d
#     docker build -f Dockerfile -t cc-rabbit-0d:prod --target production ../../
#     docker run cc-rabbit-0d:prod
#

LABEL maintainer=odeimaiz

# simcore-user uid=8004(${SC_USER_NAME}) gid=8004(${SC_USER_NAME}) groups=8004(${SC_USER_NAME})
ENV SC_USER_ID 8004
ENV SC_USER_NAME scu
RUN adduser -D -u ${SC_USER_ID} -s /bin/sh -h /home/${SC_USER_NAME} ${SC_USER_NAME}

RUN apk add --no-cache \
      su-exec \
      bash \
      jq

# -------------------------- Build stage -------------------
# Installs build/package management tools and third party dependencies
#
# + /build             WORKDIR
#

FROM base as build

ENV SC_BUILD_TARGET build

# ------------------------------------------------------------------------------------
#TODO:
# uncomment and adapt if build dependencies shall be installed
#RUN apk add --no-cache gcc git

# uncomment and adapt if python necessary
#RUN $SC_PIP install --upgrade pip wheel setuptools
# ------------------------------------------------------------------------------------

WORKDIR /build
# defines the output of the build
RUN mkdir -p /build/bin
# copy src code
COPY  src/cc-rabbit-0d src/cc-rabbit-0d
# ------------------------------------------------------------------------------------
#TODO:
# uncomment and adapt if build steps are necessary
# RUN gcc ...
# ------------------------------------------------------------------------------------

# --------------------------Cache stage -------------------
# CI in master buils & pushes this target to speed-up image build
#
#  + /build
#    + services/cc-rabbit-0d [${SC_USER_NAME}:${SC_USER_NAME}] WORKDIR
#
FROM build as cache

ENV SC_BUILD_TARGET cache



# --------------------------Production stage -------------------
# Final cleanup up to reduce image size and startup setup
# Runs as ${SC_USER_NAME} (non-root user)
#
#  + /home/${SC_USER_NAME}     $HOME = WORKDIR
#    + cc-rabbit-0d [${SC_USER_NAME}:${SC_USER_NAME}]
#    + docker [${SC_USER_NAME}:${SC_USER_NAME}]
#    + service.cli [${SC_USER_NAME}:${SC_USER_NAME}]
#
FROM base as production

ENV SC_BUILD_TARGET production
ENV SC_BOOT_MODE production


ENV INPUT_FOLDER="/input" \
    OUTPUT_FOLDER="/output" \
    LOG_FOLDER="/log"


WORKDIR /home/${SC_USER_NAME}

# ------------------------------------------------------------------------------------
#TODO:
# uncomment and adapt to install runtime dependencies
#RUN apk add --no-cache ffmpeg
# ------------------------------------------------------------------------------------

# copy binaries from cache
RUN mkdir -p cc-rabbit-0d &&\
      chown ${SC_USER_NAME}:${SC_USER_NAME} cc-rabbit-0d
COPY --from=cache /build/bin cc-rabbit-0d

# copy docker bootup scripts
COPY docker/*.sh docker/
RUN chmod +x docker/*.sh &&\
      chown ${SC_USER_NAME}:${SC_USER_NAME} docker/*.sh
# copy simcore service cli
COPY service.cli/ service.cli/
RUN chmod +x service.cli/* &&\
      chown ${SC_USER_NAME}:${SC_USER_NAME} service.cli/*
# necessary to be able to call run directly without sh in front
ENV PATH="/home/${SC_USER_NAME}/service.cli:${PATH}"

# ------------------------------------------------------------------------------------
#TODO:
# uncomment and provide a healtchecker if possible
# HEALTHCHECK --interval=30s \
#             --timeout=120s \
#             --start-period=30s \
#             --retries=3 \
#             CMD ["healthchecker app"]
# ------------------------------------------------------------------------------------

ENTRYPOINT [ "/bin/sh", "docker/entrypoint.sh" ]
CMD ["/bin/sh", "docker/boot.sh"]
