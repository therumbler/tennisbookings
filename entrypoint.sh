#!/bin/sh

exec gunicorn -b 0.0.0.0:${PORT:-5023} \
	-w 1 \
	--log-level ${LOG_LEVEL:-INFO} \
	'web:make_app()'
