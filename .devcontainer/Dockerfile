FROM mcr.microsoft.com/devcontainers/base:ubuntu

RUN apt-get update \
  && apt-get install -y --no-install-recommends python3.12 python3.12-venv python3-pip nodejs npm git \
  && npm install -g pnpm@8.15.4 \
  && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1

WORKDIR /workspaces/pg
