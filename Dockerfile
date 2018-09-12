FROM ubuntu:16.04

# Install some basic utilities
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    sudo \
    git \
    bzip2 \
    axel \
 && rm -rf /var/lib/apt/lists/*

# Create a working directory
RUN mkdir /app
WORKDIR /app

# Create a non-root user and switch to it
RUN adduser --disabled-password --gecos '' --shell /bin/bash user \
 && chown -R user:user /app
RUN echo "user ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/90-user
USER user

# All users can use /home/user as their home directory
ENV HOME=/home/user
RUN chmod 777 /home/user

# Install Miniconda
RUN curl -so ~/miniconda.sh https://repo.continuum.io/miniconda/Miniconda3-4.4.10-Linux-x86_64.sh \
 && chmod +x ~/miniconda.sh \
 && ~/miniconda.sh -b -p ~/miniconda \
 && rm ~/miniconda.sh
ENV PATH=/home/user/miniconda/bin:$PATH

# Create a Python 3.6 environment
RUN /home/user/miniconda/bin/conda install conda-build \
 && /home/user/miniconda/bin/conda create -y --name py36 python=3.6.4 \
 && /home/user/miniconda/bin/conda clean -ya
ENV CONDA_DEFAULT_ENV=py36
ENV CONDA_PREFIX=/home/user/miniconda/envs/$CONDA_DEFAULT_ENV
ENV PATH=$CONDA_PREFIX/bin:$PATH

# Ensure conda version is at least 4.4.11
# (because of this issue: https://github.com/conda/conda/issues/6811)
ENV CONDA_AUTO_UPDATE_CONDA=false
RUN conda install -y "conda>=4.4.11" && conda clean -ya

# Install FFmpeg
RUN conda install --no-update-deps -y -c conda-forge ffmpeg=3.2.4 \
 && conda clean -ya

# Install NumPy
RUN conda install --no-update-deps -y numpy=1.13.3 \
 && conda clean -ya

# Install build tools
RUN sudo apt-get update \
 && sudo apt-get install -y build-essential gfortran libncurses5-dev \
 && sudo rm -rf /var/lib/apt/lists/*

# Build and install CDF
RUN cd /tmp \
 && curl -O https://spdf.sci.gsfc.nasa.gov/pub/software/cdf/dist/cdf36_4/linux/cdf36_4-dist-all.tar.gz \
 && tar xzf cdf36_4-dist-all.tar.gz \
 && cd cdf36_4-dist \
 && make OS=linux ENV=gnu CURSES=yes FORTRAN=no UCOPTIONS=-O2 SHARED=yes all \
 && sudo make INSTALLDIR=/usr/local/cdf install

# Install other dependencies from pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# Create empty SpacePy config (suppresses an annoying warning message)
RUN mkdir /home/user/.spacepy && echo "[spacepy]" > /home/user/.spacepy/spacepy.rc

# Copy scripts into the image
COPY --chown=user:user . /app

# Set the default command to python3
CMD ["python3"]
