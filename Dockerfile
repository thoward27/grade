FROM python:3.8

# Dependencies
RUN apt-get update -qq --fix-missing && apt-get upgrade -qq \
    && apt-get install -qq \
    make \
    gcc \
    clang \
    valgrind \
    git \
    build-essential \
    software-properties-common \
    wget \
    curl

# Download and configure poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python > /dev/null
ENV PATH="/root/.poetry/bin:$PATH"
RUN poetry config virtualenvs.create false

WORKDIR /app/
COPY poetry.lock pyproject.toml /app/
RUN poetry install --no-root
COPY . /app/
RUN poetry install

CMD ["make", "test"]
