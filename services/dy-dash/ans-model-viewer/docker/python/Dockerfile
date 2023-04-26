FROM python:3.10-slim as base

LABEL maintainer=elisabettai

# simcore-user uid=8004(${SC_USER_NAME}) gid=8004(${SC_USER_NAME}) groups=8004(${SC_USER_NAME})
ENV SC_USER_ID 8004
ENV SC_USER_NAME jovyan
RUN adduser --uid ${SC_USER_ID} --disabled-password --gecos "" --shell /bin/sh --home /home/${SC_USER_NAME} ${SC_USER_NAME}

RUN apt-get update \
    && apt-get -y install --no-install-recommends \
    gosu \
    && rm --recursive --force /var/lib/apt/lists/*

RUN pip --no-cache --quiet install --upgrade \
  pip \
  setuptools \
  wheel

FROM base as production

ENV SC_BUILD_TARGET production
ENV SC_BOOT_MODE production

WORKDIR /home/${SC_USER_NAME}

# copy src code and requirements
COPY --chown=${SC_USER_NAME}:${SC_USER_NAME} src/ans_model_viewer src/ans_model_viewer

RUN pip install pip-tools && \
  pip-compile --build-isolation --output-file src/ans_model_viewer/requirements.txt src/ans_model_viewer/requirements.in  && \
  pip --no-cache install -r src/ans_model_viewer/requirements.txt && \
  rm src/ans_model_viewer/requirements.in

# copy docker bootup scripts
COPY --chown=${SC_USER_NAME}:${SC_USER_NAME} docker/*bash docker/
# copy simcore service cli
COPY --chown=${SC_USER_NAME}:${SC_USER_NAME} service.cli/ service.cli/
# necessary to be able to call run directly without sh in front
ENV PATH="/home/${SC_USER_NAME}/service.cli:${PATH}"

# ------------------------------------------------------------------------------------
HEALTHCHECK --interval=30s \
             --timeout=120s \
             --start-period=30s \
             --retries=3 \
             CMD ["healthchecker app"]
# ------------------------------------------------------------------------------------

EXPOSE 8888

ENTRYPOINT [ "/bin/bash", "docker/entrypoint.bash"]
CMD ["run"]
