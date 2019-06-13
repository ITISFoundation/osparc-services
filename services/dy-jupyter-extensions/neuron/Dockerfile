ARG BASE_IMAGE
FROM ${BASE_IMAGE} AS common
LABEL maintainer="guidon"

USER root

# NEURON requirements
RUN apt-get update &&\
  apt-get install --no-install-recommends -y \
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
RUN mkdir /opt/conda/neuron && \
  npm config set package-lock 0 && \
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

# install netpyne
# RUN git clone https://github.com/Neurosim-lab/netpyne.git && \
#   cd netpyne && git checkout development && pip install -e .

#
# install requirements --------------------------------------------------------
COPY --chown=jovyan:users ./requirements/prod.txt requirements.txt
RUN pip --no-cache install -r requirements.txt

# prepare for booting ---------------------------------------------------------
# COPY --chown=jovyan:users docker /docker
# where to put the inputs outputs
ENV INPUTS_FOLDER /home/jovyan/notebooks/_inputs
ENV OUTPUTS_FOLDER /home/jovyan/notebooks/_outputs
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
