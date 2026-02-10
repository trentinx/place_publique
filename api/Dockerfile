FROM python:3.13-bullseye


RUN useradd -m -U user; \ 
    apt update; \
    apt upgrade; \
    apt install -y build-essential supervisor htop vim


RUN mkdir -p /var/log/hypercorn
RUN touch /var/log/supervisord.log /var/log/hypercorn/access.log /var/log/hypercorn/error.log
RUN chown user:user /var/log/supervisord.log /var/log/hypercorn/access.log /var/log/hypercorn/error.log


WORKDIR /home/user 

ENV MODE=prod

COPY --chown=user api app
RUN mv app/Makefile Makefile


USER user
RUN pip install -U pip
RUN make install

EXPOSE 80

ENTRYPOINT [ "make","service-up" ]
