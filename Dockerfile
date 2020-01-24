FROM python:3.7-alpine3.11 AS base
LABEL maintainer "Just a baka <justabaka@gmail.com>"

# Build dependencies
FROM base as builder
RUN mkdir /install
WORKDIR /install

RUN apk update \
	&& apk add gcc python3-dev libffi-dev musl-dev openssl-dev \
	&& rm -rf /var/cache/apk/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Build the final image
FROM base
COPY --from=builder /install /usr/local

ENV PYTHONUNBUFFERED=1 \
	BOT_TOKEN="" \
	CHAT_ID="" \
	LOG_LEVEL="INFO"

WORKDIR /alertmanager-webhook-telegram
COPY flaskAlert.py .
COPY templates/* templates/

EXPOSE 8080
USER nobody

ENTRYPOINT ["/usr/local/bin/gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "flaskAlert:app"]
