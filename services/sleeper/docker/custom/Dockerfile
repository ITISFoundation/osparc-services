# syntax=docker/dockerfile:1
ARG BASE_IMAGE="nvidia/cuda:12.0.0-base-ubuntu22.04"
FROM ${BASE_IMAGE} as base
#
#  USAGE:
#     cd services/sleeper
#     docker build -f Dockerfile -t sleeper:prod --target production ../../
#     docker run sleeper:prod
#

LABEL maintainer=sanderegg

# simcore-user uid=8004(${SC_USER_NAME}) gid=8004(${SC_USER_NAME}) groups=8004(${SC_USER_NAME})
ENV SC_USER_ID=8004 \
    SC_USER_NAME=scu \
    SC_BUILD_TARGET=base

RUN adduser \
    --uid ${SC_USER_ID} \
    --disabled-password \
    --gecos "" \
    --shell /bin/sh \
    --home /home/${SC_USER_NAME} ${SC_USER_NAME}

# Sets utf-8 encoding for Python et al
ENV LANG=C.UTF-8

# Turns off writing .pyc files; superfluous on an ephemeral container.
ENV PYTHONDONTWRITEBYTECODE=1 \
    VIRTUAL_ENV=/home/scu/.venv

# Ensures that the python and pip executables used in the image will be
# those from our virtualenv.
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

RUN --mount=type=cache,target=/var/cache/apt,mode=0755,sharing=private \
    --mount=type=cache,target=/var/lib/apt,mode=0755,sharing=private \
    set -eux \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    jq \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*;

# Define an argument that dictates whether to run the installation commands
ARG INSTALL_EXTRAS=false
RUN --mount=type=cache,target=/var/cache/apt,mode=0755,sharing=private \
    --mount=type=cache,target=/var/lib/apt,mode=0755,sharing=private \
    if [ "$INSTALL_EXTRAS" = "true" ]; then \
    set -eux \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*; \
    fi

# for ARM architecture this helps a lot VS building packages
ENV PIP_EXTRA_INDEX_URL=https://www.piwheels.org/simple



# -------------------------- Build stage -------------------
# Installs build/package management tools and third party dependencies
#
# + /build             WORKDIR
#

FROM base as build

ENV SC_BUILD_TARGET=build

# NOTE: install https://github.com/astral-sh/uv ultra-fast rust-based pip replacement
RUN --mount=type=cache,mode=0755,target=/root/.cache/pip \
    pip install uv~=0.1

# NOTE: python virtualenv is used here such that installed
# packages may be moved to production image easily by copying the venv
RUN uv venv "${VIRTUAL_ENV}"

RUN --mount=type=cache,mode=0755,target=/root/.cache/pip \
    uv pip install --upgrade  \
    pip~=24.0  \
    wheel \
    setuptools

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

ENV SC_BUILD_TARGET=production \
    SC_BOOT_MODE=production

ENV PYTHONOPTIMIZE=TRUE


ENV INPUT_FOLDER="/input" \
    OUTPUT_FOLDER="/output"

WORKDIR /home/${SC_USER_NAME}
# ensure home folder is read/writable for user scu
RUN chown -R ${SC_USER_NAME} /home/${SC_USER_NAME}
# Starting from clean base image, copies pre-installed virtualenv from prod-only-deps
COPY --chown=${SC_USER_NAME}:${SC_USER_NAME} --from=build  ${VIRTUAL_ENV} ${VIRTUAL_ENV}

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
