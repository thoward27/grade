FROM python:3.8.0

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
    curl 

# Install grade
RUN mkdir /app/
COPY . /app/
RUN python -m pip install /app/
RUN python -m pip install -r /app/requirements.txt

# Defaults
WORKDIR /app/
CMD ["python", "-m", "unittest", "discover"]
