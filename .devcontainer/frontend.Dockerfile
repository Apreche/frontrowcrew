ARG VARIANT=22-bookworm
FROM mcr.microsoft.com/vscode/devcontainers/javascript-node:${VARIANT}

RUN apt-get update \
    && apt-get --no-install-recommends -y install \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
COPY ../package.json /workspace/package.json
RUN npm install --no-fund --silent -g npm@latest
RUN npm install --no-fund --silent
