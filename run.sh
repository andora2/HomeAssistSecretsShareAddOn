#!/usr/bin/with-contenv bashio
# with-contenv/bashio ist HAs Standard-Startumgebung fuer Add-ons.
# Braucht man hier kaum, ist aber der uebliche, sichere Weg.
bashio::log.info "Secret Share startet auf Port 8099 (Ingress) ..."
exec python3 /share.py
