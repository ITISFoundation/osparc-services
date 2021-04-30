#!/bin/sh

SCRIPT_NAME=$SIMCORE_NODE_BASEPATH gunicorn -b 0.0.0.0:80 httpbin:app -k gevent --log-level DEBUG