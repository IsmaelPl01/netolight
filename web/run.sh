#!/bin/bash

envsubst "\$NL_API_HOST,\$NL_API_PORT" < /etc/nl-web/nginx.conf.template > /etc/nginx/nginx.conf

nginx -g "daemon off;"
