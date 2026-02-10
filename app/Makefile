.PHONY: install service-up service-down
SHELL := /bin/bash


install:
#	@pip install git+https://github.com/trentinx/place_publique
	@pip install flask hypercorn

service-up:
	@supervisord -c app/supervisor.conf

service-down:
	@pkill 'supervisord'	



# docker run -d -p 8080:8080 --name flask xavier_flask_test:1.0
# docker rm flask