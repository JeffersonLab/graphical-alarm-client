FROM python:3.7-slim

ARG CUSTOM_CRT_URL

WORKDIR /

RUN apt-get update \
    && apt-get install -y librdkafka-dev wget git bash curl jq gcc python3-tk vim \
    && git clone https://github.com/JeffersonLab/graphical-alarm-client \
    && cd ./graphical-alarm-client/scripts \
    && mkdir /scripts \
    && cp * /scripts \
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

WORKDIR /scripts

ENTRYPOINT ["python"]
CMD ["hello.py"]