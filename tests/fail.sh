#!/bin/sh

curl \
--request POST \
--data '{invalid json}' \
localhost:8080
