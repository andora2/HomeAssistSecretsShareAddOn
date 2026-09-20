# BUILD_FROM wird vom HA-Supervisor je nach Prozessor-Typ automatisch gesetzt
# (das passende Alpine-Basis-Image). Deshalb kein fester FROM-Wert.
ARG BUILD_FROM
FROM ${BUILD_FROM}

# Python aus dem Alpine-Paketmanager - kein pip, keine Fremdpakete.
RUN apk add --no-cache python3

COPY run.sh /
COPY share.py /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
