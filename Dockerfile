FROM gradescope/auto-builds:latest as base

RUN apt-get -y update --fix-missing && apt-get -y upgrade
RUN apt-get update && apt-get install -y \
    make \
    clang \
    gcc \
    valgrind \
    netpbm \
    libnetpbm10-dev \
    software-properties-common \
    libsigsegv2 \
    libsigsegv-dev \
    libjpeg-dev \
    libjpeg-progs \
    python3-pip

# Python 3.8 patch.
RUN add-apt-repository ppa:deadsnakes/ppa && apt-get update && apt-get install -y python3.8 python3.8-distutils

COPY . /autograder/source/
COPY run_autograder /autograder/

# CII
RUN cd /autograder/source/cii && /bin/sh /autograder/source/cii/install-cii.sh

# PNM Reader
RUN cd /autograder/source/pnmrdr && make && make install

# Unblack Testing
RUN cd /autograder/source/unblacktest && /bin/sh compile && cp unblacktest /usr/local/bin/

RUN mkdir /autograder/results

RUN python3.8 -m pip install gradescope-utils
WORKDIR /autograder
ENTRYPOINT ["sh"]
CMD ["run_autograder"]

COPY ./solution/ /autograder/submission/
