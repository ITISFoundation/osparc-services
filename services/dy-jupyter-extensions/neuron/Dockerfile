ARG BASE_IMAGE
FROM ${BASE_IMAGE} AS common
LABEL maintainer="guidon"

USER root

# NEURON requirements
RUN apt-get update &&\
  apt-get install -y \
    automake \
    bison \
    bzip2 \
    ca-certificates \
    curl \
    flex \
    g++ \
    git \
    libncurses-dev \
    libpng-dev \
    libreadline-dev \
    libtool \
    openmpi-bin \
    libopenmpi-dev \
    make &&\
  rm -rf /root/.cache &&\
  rm -rf /var/lib/apt/lists/* /var/log/dpkg.log

USER $NB_USER

# install NEURON from github
RUN mkdir /opt/conda/neuron &&\
  npm config set package-lock 0 &&\
  cd /tmp &&\
  git clone --depth 1 -b 7.6.7 https://github.com/neuronsimulator/nrn &&\
  cd nrn &&\
  ./build.sh &&\
  ./configure \
    --without-x \
    --with-nrnpython=python3 \
    --with-paranrn \
    --prefix='/opt/conda/neuron' \
    --without-iv \
    --without-nrnoc-x11 \
    --silent &&\
  make --silent -j4 &&\
  make --silent install -j4 &&\
  cd src/nrnpython &&\
  python setup.py install &&\
  cd / &&\
  rm -rf /tmp/* &&\
  rm -rf /opt/conda/pkgs &&\
  conda clean -tipsy

# nrnivmodl
ENV PATH /opt/conda/neuron/x86_64/bin:$PATH 

# needed for netpyne
RUN pip install pyneuroml

# install netpyne
RUN git clone https://github.com/Neurosim-lab/netpyne.git && \  
  cd netpyne && git checkout development && pip install -e . 



# 
# install requirements --------------------------------------------------------
COPY --chown=jovyan:users requirements.txt .
# TODO: tmp workaround for https://github.com/pypa/pip/issues/6197
RUN pip --cache-dir=/tmp/.pipcache install -r requirements.txt &&\
     rm -rf /tmp/.pipcache
# prepare for booting ---------------------------------------------------------
COPY --chown=jovyan:users docker /docker
# copy some helper scripts-----------------------------------------------------
COPY --chown=jovyan:users scripts /scripts
ENV PYTHONPATH=/scripts:$PYTHONPATH
# set of arguments to copy the right notebook ---------------------------------
ARG NOTEBOOK_NAME
ENV NOTEBOOK_URL=${NOTEBOOK_NAME}
# -----------------------------------------------------------------------------
FROM common AS development
VOLUME /home/jovyan/services
VOLUME /home/jovyan/scripts/dy_services_helpers
VOLUME /home/jovyan/devel-config
VOLUME /home/jovyan/notebooks
ENV USE_CASE_CONFIG_FILE="node_configuration_file.json"
ENV INIT_OPTIONS="5000 200 20 tab"
ENV CREATE_DUMMY_TABLE=1
# switch off the default entrypoint
ENTRYPOINT []
CMD [ "/bin/bash", "/docker/boot.sh" ]
# -----------------------------------------------------------------------------
FROM common AS production
# set of arguments to copy the right notebook
ARG NOTEBOOK_NAME
ARG NOTEBOOK_FOLDER_NAME
# copy the notebook in the image
COPY --chown=jovyan:users ${NOTEBOOK_FOLDER_NAME}/${NOTEBOOK_NAME} notebooks/${NOTEBOOK_NAME}
ENTRYPOINT [ "/bin/bash", "/docker/boot.sh" ]
