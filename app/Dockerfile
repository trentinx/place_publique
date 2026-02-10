FROM python:3.13-bullseye


RUN useradd -m -U user; \ 
    apt update; \
    apt upgrade; \
    apt install -y build-essential supervisor htop vim


RUN mkdir -p /var/log/hypercorn
RUN touch /var/log/supervisord.log /var/log/hypercorn/flask_access.log /var/log/hypercorn/flask_error.log
RUN chown user:user /var/log/supervisord.log /var/log/hypercorn/flask_access.log /var/log/hypercorn/flask_error.log


WORKDIR /home/user 

ENV MODE=prod

COPY --chown=user app app
COPY --chown=user ../Makefile  .


USER user
RUN pip install -U pip
RUN make install

EXPOSE 8080

ENTRYPOINT [ "make","flask-up" ]
