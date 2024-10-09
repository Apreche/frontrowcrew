# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.10, 3.9, 3.8, 3.7, 3.6, 3-bullseye, 3.10-bullseye, 3.9-bullseye, 3.8-bullseye, 3.7-bullseye, 3.6-bullseye, 3-buster, 3.10-buster, 3.9-buster, 3.8-buster, 3.7-buster, 3.6-buster
ARG VARIANT=3.11
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

ARG APP_ENV=localdev

ENV APP_ENV=${APP_ENV} \
    PATH="$PATH:/root/.local/bin" \
    DEBIAN_FRONTEND=noninteractive \
    # Python
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # PIP
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_CACHE_DIR=off \
    # Poetry
    POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_IN_PROJECT=1

RUN apt-get update \
    && apt-get --no-install-recommends -y install \
    bash-completion \
    ftp \
    libexempi8 \
    libmemcached-dev \
    postgresql-client \
    sqlite3 \
    && pip${VARIANT} install \
    "poetry~=${POETRY_VERSION}" \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

COPY .devcontainer/django_bash_completion /etc/bash_completion.d/
COPY .devcontainer/.sqliterc /home/vscode/
