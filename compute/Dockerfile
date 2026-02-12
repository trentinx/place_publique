FROM python:3.13-bullseye


RUN useradd -m -U user; \ 
    apt update; \
    apt upgrade; \
    apt install -y build-essential htop libgl1 libglib2.0-0 libxcb1 vim

WORKDIR /home/user 
COPY --chown=user scripts/ ./scripts/

USER user

RUN echo "export PATH=\$PATH:~/.local/bin" >> ~/.bashrc
RUN pip install -U pip
RUN pip install ultralytics mlflow python-dotenv requests;

ENTRYPOINT [ "/bin/bash" ]
