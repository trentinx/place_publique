.PHONY: clean install install-dev
SHELL := /bin/bash
MODE ?= dev

clean:
	@for file in ".ipynb_checkpoints" "*.egg-info" "__pycache__" "upload"; do \
    	find -name  $$file | xargs rm -fr; \
	done;
		
install:
	@uv pip install  .

install-dev:
	@uv pip install -e .

flask-up:
ifeq ($(MODE),dev)
	@python app/main.py
else
	@supervisord -c app/supervisor.conf
endif

flask-down:
ifeq ($(MODE),dev)
	@pkill 'python'
else
	@pkill 'supervisord'
endif