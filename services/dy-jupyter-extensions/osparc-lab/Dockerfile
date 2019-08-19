ARG BASE_IMAGE
FROM ${BASE_IMAGE} AS common
LABEL maintainer="guidon"

USER root

# install requirements --------------------------------------------------------
# COPY --chown=jovyan:users ./requirements/prod.txt requirements.txt
# RUN pip --no-cache install -r requirements.txt

# prepare for booting ---------------------------------------------------------
# COPY --chown=jovyan:users docker /docker
# where to put the inputs outputs
ENV INPUTS_FOLDER /home/jovyan/notebooks/_inputs
ENV OUTPUTS_FOLDER /home/jovyan/notebooks/_outputs
ENV JUPYTER_ENABLE_LAB 1

# VS CODE ---------------------------------------------------------------------
USER $NB_USER

RUN pip install --no-cache-dir \
    keras-rl pyopengl \
    gym[atari] ray[rllib] roboschool \
    jupyter-vscode-server jedi pysc2 \
    python-language-server[yapf] \
    setuptools wheel && \
    pip uninstall opencv-python opencv-python-headless opencv-contrib-python -y && \
    pip install --no-cache-dir opencv-contrib-python -U && \
    rm -rf /tmp/* && \
    rm -rf $HOME/.cache && \
    rm -rf $HOME/.node-gyp && \
    fix-permissions $CONDA_DIR && \
    fix-permissions $HOME

USER root

ENV CODESERVER_URL="https://github.com/cdr/code-server/releases/download/1.1156-vsc1.33.1/code-server1.1156-vsc1.33.1-linux-x64.tar.gz" \
    CODESERVER="code-server1.1156-vsc1.33.1-linux-x64"

RUN wget ${CODESERVER_URL} && \
    tar xvf ${CODESERVER}.tar.gz && \
    mv ${CODESERVER}/code-server /usr/local/bin/ && \
    rm -rf code-server* && \
    rm -rf /tmp/* && \
    rm -rf $HOME/.cache && \
    rm -rf $HOME/.node-gyp && \
    fix-permissions $CONDA_DIR && \
    fix-permissions $HOME

USER $NB_UID
# -----------------------------------------------------------------------------
FROM common AS development
VOLUME /home/jovyan/services
VOLUME /home/jovyan/scripts/dy_services_helpers
VOLUME /home/jovyan/devel-config
VOLUME /home/jovyan/notebooks
# switch off the default entrypoint
ENTRYPOINT []
CMD [ "/bin/bash", "/docker/boot.sh" ]
# -----------------------------------------------------------------------------
FROM common AS production
# copy the notebooks in the image
COPY --chown=jovyan:users ${NOTEBOOK_FOLDER_NAME} notebooks
ENTRYPOINT [ "/bin/bash", "/docker/boot.sh" ]
