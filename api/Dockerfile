#FROM python:3.13-bullseye
FROM ultralytics/ultralytics:8.4.22-python-export

RUN useradd -m -U user; \ 
    apt update; \
    apt upgrade; \
    apt install -y build-essential supervisor htop vim libgl1 iputils-ping procps


RUN mkdir -p /var/log/hypercorn
RUN touch /var/log/supervisord.log /var/log/hypercorn/access.log /var/log/hypercorn/error.log
RUN chown user:user /var/log/supervisord.log /var/log/hypercorn/access.log /var/log/hypercorn/error.log

WORKDIR /home/user

ENV MODE=prod
COPY --chown=user api app
COPY --chown=user config.json .
COPY --chown=user src src
COPY --chown=user pyproject.toml .

USER user

RUN mv app/Makefile Makefile
RUN mkdir model
COPY --chown=user runs/detect/train/weights/best.pt ./model/yolo.pt
RUN pip install -U pip
RUN make install

EXPOSE 80

ENTRYPOINT [ "make","service-up" ]
