
ARG BASE_IMAGE="nvidia/cuda:10.0-base-ubuntu18.04"
FROM ${BASE_IMAGE} as base
#
#  USAGE:
#     cd services/sleeper
#     docker build -f Dockerfile -t sleeper:prod --target production ../../
#     docker run sleeper:prod
#

LABEL maintainer="Andrei Neagu <neagu@itis.swiss>"

# simcore-user uid=8004(${SC_USER_NAME}) gid=8004(${SC_USER_NAME}) groups=8004(${SC_USER_NAME})
ENV SC_USER_ID 8004
ENV SC_USER_NAME scu
RUN adduser --uid ${SC_USER_ID} --disabled-password --gecos "" --shell /bin/sh --home /home/${SC_USER_NAME} ${SC_USER_NAME}

RUN apt-get update --fix-missing && \
    apt-get install -y wget bzip2 ca-certificates curl git python3 python3-pip jq && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# for ARM architecture this helps a lot VS building packages
ENV PIP_EXTRA_INDEX_URL=https://www.piwheels.org/simple



# -------------------------- Build stage -------------------
# Installs build/package management tools and third party dependencies
#
# + /build             WORKDIR
#

FROM base as build

ENV SC_BUILD_TARGET build

# Instlling python
RUN pip3 install --upgrade pip wheel setuptools

# ------------------------------------------------------------------------------------

WORKDIR /build
# defines the output of the build
RUN mkdir --parents /build/bin
# copy src code
COPY --chown=${SC_USER_NAME}:${SC_USER_NAME} src/sleeper src/sleeper
# ------------------------------------------------------------------------------------

RUN cp -R src/sleeper/* /build/bin
# ------------------------------------------------------------------------------------

# --------------------------Production stage -------------------
# Final cleanup up to reduce image size and startup setup
# Runs as ${SC_USER_NAME} (non-root user)
#
#  + /home/${SC_USER_NAME}     $HOME = WORKDIR
#    + sleeper [${SC_USER_NAME}:${SC_USER_NAME}]
#    + docker [${SC_USER_NAME}:${SC_USER_NAME}]
#    + service.cli [${SC_USER_NAME}:${SC_USER_NAME}]
#
FROM base as production

ENV SC_BUILD_TARGET production
ENV SC_BOOT_MODE production


ENV INPUT_FOLDER="/input" \
    OUTPUT_FOLDER="/output"

WORKDIR /home/${SC_USER_NAME}

# copy docker bootup scripts
COPY --chown=${SC_USER_NAME}:${SC_USER_NAME} docker/custom/*.sh docker/
# copy simcore service cli
COPY --chown=${SC_USER_NAME}:${SC_USER_NAME} service.cli/ service.cli/
# necessary to be able to call run directly without sh in front
ENV PATH="/home/${SC_USER_NAME}/service.cli:${PATH}"

# copy binaries from build
COPY --from=build --chown=${SC_USER_NAME}:${SC_USER_NAME} /build/bin sleeper

ENTRYPOINT [ "/bin/sh", "docker/entrypoint.sh", "/bin/sh", "-c" ]
CMD ["run"]
