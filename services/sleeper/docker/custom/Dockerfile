# syntax=docker/dockerfile:1
ARG BASE_IMAGE="python:3.14-slim"
ARG PYTHON_VERSION=3.14

FROM ghcr.io/astral-sh/uv:0.12.8 AS uv

FROM ${BASE_IMAGE} AS base
#
#  USAGE:
#     cd services/sleeper
#     docker build -f Dockerfile -t sleeper:prod --target production ../../
#       docker run sleeper:prod
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
    gosu \
    fd-find \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    # verify that the binary works
    && gosu nobody true

# for ARM architecture this helps a lot VS building packages
ENV UV_EXTRA_INDEX_URL=https://www.piwheels.org/simple



# -------------------------- Build stage -------------------
# Installs build/package management tools and third party dependencies
#
# + /build             WORKDIR
#

FROM base AS build

ARG PYTHON_VERSION

ENV SC_BUILD_TARGET=build

# NOTE: uv (https://github.com/astral-sh/uv) ultra-fast rust-based pip replacement,
# copied from the official distroless image, pinned to a specific version
# (see https://docs.astral.sh/uv/guides/integration/docker/#installing-uv)
COPY --from=uv /uv /uvx /bin/

# NOTE: python virtualenv is used here such that installed
# packages may be moved to production image easily by copying the venv.
# uv reuses the base image's system Python (all 3 variants share the same
# python:slim image, so no standalone interpreter download is ever needed).
RUN --mount=type=cache,mode=0755,target=/root/.cache/uv \
    uv venv --python "${PYTHON_VERSION}" "${VIRTUAL_ENV}"

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
FROM base AS production

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
