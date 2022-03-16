FROM python:3.9-slim

ARG CUSTOM_CRT_URL

WORKDIR /

RUN useradd -r -m -s /bin/bash guiuser

RUN apt-get update \
    && apt-get install -y librdkafka-dev wget git bash curl jq gcc python3-tk python3-pyqt5 vim

RUN git clone https://github.com/JeffersonLab/graphical-alarm-client \
    && cd ./graphical-alarm-client/scripts \
    && mkdir /scripts \
    && cp -r * /scripts \
    && cd / \
    && chmod -R +x /scripts \
    && if [ -z "$CUSTOM_CRT_URL" ] ; then echo "No custom cert needed"; else \
          wget -O /usr/local/share/ca-certificates/customcert.crt $CUSTOM_CRT_URL \
          && update-ca-certificates \
          && export OPTIONAL_CERT_ARG=--cert=/etc/ssl/certs/ca-certificates.crt \
          ; fi \
    && pip install --upgrade pip $OPTIONAL_CERT_ARG \
    && pip install --no-cache-dir -r ./graphical-alarm-client/requirements.txt $OPTIONAL_CERT_ARG \
    && rm -rf ./graphical-alarm-client

## For now, we just install this missing dependency manually downloaded from https://download.opensuse.org/repositories/home:/stevenpusser:/libxcb-util1/Debian_9.0/amd64/libxcb-util1_0.4.0-0.1~obs_amd64.deb
RUN dpkg -i /scripts/libxcb-util1_0.4.0-0.1_obs_amd64.deb \
    && apt-get update -y \
    && apt-get install -f

WORKDIR /scripts

USER guiuser