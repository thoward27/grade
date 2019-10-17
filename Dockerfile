FROM gradescope/auto-builds:latest as base

# First let's just get things updated.
RUN apt-get -y update --fix-missing && apt-get -y upgrade

# Dependancies
RUN apt-get install -y \
    make \
    gcc \
    clang \
    valgrind \
    git \
    build-essential \
    software-properties-common \
    wget \
    curl \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libffi-dev \
    liblzma-dev \
    libsqlite3-dev \
    llvm \
    xz-utils \
    python-openssl

# Install pyenv
RUN curl https://pyenv.run | bash
ENV PATH /root/.pyenv/shims:/root/.pyenv/bin:$PATH

RUN pyenv install 3.8.0 && pyenv global 3.8.0 && pyenv rehash

# Python 3.8 patch.
# RUN add-apt-repository ppa:deadsnakes/ppa && apt-get update && apt-get install -y python3.8 python3.8-distutils

RUN python -m pip install gradescope-utils

ENTRYPOINT ["bash"]
CMD ["python"]
