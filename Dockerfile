# Festes, oeffentliches Python-Basis-Image - kein BUILD_FROM noetig,
# baut auf amd64 (N100) genauso wie auf aarch64 (HA Green) gleich.
FROM python:3-alpine

COPY share.py /

# Direkt starten - kein bashio/s6 noetig fuer diesen Mini-Dienst.
CMD [ "python3", "/share.py" ]
