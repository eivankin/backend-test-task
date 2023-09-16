FROM python:3.11-alpine AS builder
ARG SERVICE_NAME

RUN apk update && \
    apk upgrade && \
    apk add --no-cache gcc make musl-dev && \
    python -m venv /opt/venv

# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app
COPY ./common/requirements.txt ./common/requirements.txt
COPY ./${SERVICE_NAME}/requirements.txt ./${SERVICE_NAME}/requirements.txt
RUN pip install --no-cache-dir -r ./common/requirements.txt -r ./${SERVICE_NAME}/requirements.txt

FROM python:3.11-alpine AS development
ARG SERVICE_NAME
COPY --from=builder /opt/venv /opt/venv

# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app
ARG SERVICE_NAME
COPY ./common/ ./common/
COPY ./${SERVICE_NAME}/ ./${SERVICE_NAME}/
ENV PYTHONPATH="/app:${PYTHONPATH}"
