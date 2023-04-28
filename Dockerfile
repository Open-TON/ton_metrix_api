FROM python:3.11.0-alpine3.17 as python-base

ARG THIS_ENV
ENV THIS_ENV=${THIS_ENV} \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    APP_PATH="/app" \
    POETRY_VERSION=1.4.1

RUN pip install -U pip setuptools &&  \
    pip install poetry==${POETRY_VERSION}

RUN mkdir -p ${APP_PATH}

WORKDIR $APP_PATH
COPY . .
RUN poetry lock
RUN poetry install --no-root --without dev
# 'development' stage installs all dev deps and can be used to develop code.
# For example using docker-compose to mount local volume under /app

ENV FASTAPI_ENV=development

RUN chmod +x ./docker-entrypoint.sh

WORKDIR ./src

EXPOSE 8000
ENTRYPOINT ../docker-entrypoint.sh $0 $@
CMD ["uvicorn", "--reload", "--factory", "--host=0.0.0.0", "--port=8000", "main:app"]
# added factory