.PHONY: install service-up service-down
SHELL := /bin/bash


install:
#	@pip install git+https://github.com/trentinx/place_publique
	@pip install  . ".[app]"

service-up:
	@supervisord -c app/supervisor.conf

service-down:
	@pkill 'supervisord'	

