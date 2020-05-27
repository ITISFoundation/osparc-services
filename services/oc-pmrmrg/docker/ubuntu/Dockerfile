FROM ubuntu:18.04 as base
#
#  USAGE:
#     cd services/pmr_mrg
#     docker build -f Dockerfile -t pmr_mrg:prod --target production ../../
#     docker run pmr_mrg:prod

RUN apt-get -qq update && apt-get install -y \
 libpulse-mainloop-glib0 \
 libfontconfig1 \
 libfreetype6 \
 libx11-6 \
 libx11-xcb1 \
 libxext6 \
 libxslt1.1 \
 sqlite3

RUN apt-get -qq update && \
    apt-get install -y \
      jq    &&\
    rm -rf /var/lib/apt/lists/*

WORKDIR /home/opencor

# Taking the OpenCOR binary from the web, this binary is Python enabled.  This method fails to complete for me so enabling the alternative method.
# ADD https://github.com/dbrnz/opencor/releases/download/snapshot-2019-06-11/OpenCOR-2019-06-11-Linux.tar.gz /home/opencor/
# RUN tar -xvzf OpenCOR-2019-06-11-Linux.tar.gz && #     rm OpenCOR-2019-06-11-Linux.tar.gz

ADD https://opencor.ws/downloads/snapshots/2020-02-14/OpenCOR-2020-02-14-Linux.tar.gz /home/opencor/
RUN tar -xvzf OpenCOR-2020-02-14-Linux.tar.gz &&     rm OpenCOR-2020-02-14-Linux.tar.gz

#

LABEL maintainer=KZzizzle

# simcore-user uid=8004(${SC_USER_NAME}) gid=8004(${SC_USER_NAME}) groups=8004(${SC_USER_NAME})
ENV SC_USER_ID 8004
ENV SC_USER_NAME scu
RUN adduser --uid ${SC_USER_ID} --disabled-password --gecos "" --shell /bin/sh --home /home/${SC_USER_NAME} ${SC_USER_NAME}

COPY --chown=scu:scu ./src/pmr_mrg/ /home/pmr_mrg/

RUN apt-get update \
    && apt-get -y install --no-install-recommends \
    jq \
    && rm --recursive --force /var/lib/apt/lists/*

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
#RUN apt-get update \
# && apt-get -y install --no-install-recommends \
# gcc \
# git \
# && rm -rf /var/lib/apt/lists/*

# uncomment and adapt if python necessary
#RUN $SC_PIP install --upgrade pip wheel setuptools
# ------------------------------------------------------------------------------------

WORKDIR /build
# defines the output of the build
RUN mkdir --parents /build/bin
# copy src code
COPY --chown=${SC_USER_NAME}:${SC_USER_NAME} src/pmr_mrg src/pmr_mrg
# ------------------------------------------------------------------------------------
#TODO:
# uncomment and adapt if build steps are necessary
# RUN cp -R src/pmr_mrg/* /build/bin
# ------------------------------------------------------------------------------------

# --------------------------Production stage -------------------
# Final cleanup up to reduce image size and startup setup
# Runs as ${SC_USER_NAME} (non-root user)
#
#  + /home/${SC_USER_NAME}     $HOME = WORKDIR
#    + pmr_mrg [${SC_USER_NAME}:${SC_USER_NAME}]
#    + docker [${SC_USER_NAME}:${SC_USER_NAME}]
#    + service.cli [${SC_USER_NAME}:${SC_USER_NAME}]
#
FROM base as production

ENV SC_BUILD_TARGET production
ENV SC_BOOT_MODE production


ENV INPUT_FOLDER="/input" \
    OUTPUT_FOLDER="/output"


WORKDIR /home/${SC_USER_NAME}

# ------------------------------------------------------------------------------------
#TODO:
# uncomment and adapt to install runtime dependencies
#RUN apt-get update \
# && apt-get -y install --no-install-recommends \
# && rm -rf /var/lib/apt/lists/*
# ------------------------------------------------------------------------------------

# copy docker bootup scripts
COPY --chown=${SC_USER_NAME}:${SC_USER_NAME} docker/ubuntu/*.sh docker/
# copy simcore service cli
COPY --chown=${SC_USER_NAME}:${SC_USER_NAME} service.cli/ service.cli/
# necessary to be able to call run directly without sh in front
ENV PATH="/home/${SC_USER_NAME}/service.cli:${PATH}"

# copy binaries from build
COPY --from=build --chown=${SC_USER_NAME}:${SC_USER_NAME} /build/bin pmr_mrg

# ------------------------------------------------------------------------------------
#TODO:
# uncomment and provide a healtchecker if possible
# HEALTHCHECK --interval=30s \
#             --timeout=120s \
#             --start-period=30s \
#             --retries=3 \
#             CMD ["healthchecker app"]
# ------------------------------------------------------------------------------------

ENTRYPOINT [ "/bin/sh", "docker/entrypoint.sh", "/bin/sh", "-c" ]
CMD ["run"]
