# Kontext / Übergabe: Secret-Share HA-Add-on

Handoff-Dokument für die Weiterarbeit in VSCode / Claude Code.

## Ziel & eigentlicher Zweck

- **Oberflächlich:** ein winziger Web-Dienst, um Text/Passwörter zwischen Adrians
  Geräten (Laptop, iPhone, Android-Tablet, weitere Win/Mac-Laptops) im LAN zu
  teilen, statt sie sich per WhatsApp zu schicken. Inhalt soll **spurlos** sein
  (nur im RAM, keine Logs).
- **Eigentlicher Zweck:** Der Use Case ist bewusst klein gewählt und dient als
  **Testballon**, um die **Verwaltbarkeit und Erweiterbarkeit von Home Assistant
  als Plattform** zu bewerten (Add-on/App-Mechanik, Ingress, Bau-Schleife).
  Beim Bewerten von Entscheidungen also diese Brille aufsetzen, nicht nur
  „läuft das Skript".

## Umgebung (Stand jetzt)

- HA läuft **demo-mäßig als HA OS in einer VM auf einem Win11-Laptop** – nur an,
  wenn der Laptop an ist. **Kein Always-on-Host.** Bewusst nur Spielwiese.
- Supervisor **2026.09.2**, HA OS **18.3**, Maschine **qemux86-64 (amd64)**.
- Wichtig: HA hat mit **2026.2 „Add-ons" in „Apps" umbenannt**. Menü:
  Einstellungen → **Apps** → App Store. Konfig-Format behält intern die alte
  `addon`-Benennung (Rückwärtskompatibilität).
- **Zielsystem später:** lüfterloser **N100/N150 Mini-PC** ODER **HA Green**.
  Offene Hardware-Entscheidung – siehe „Offene Punkte".

## Was existiert (GitHub-Repo, als HA-App-Quelle angebunden)

Repo ist inzwischen **public** (Add-on-Quellen müssen erreichbar sein).
Struktur:

    repo-wurzel/
      repository.yaml            # markiert Repo als App-/Add-on-Quelle
      secret_share/
        config.yaml              # Manifest (slug: secret_share)
        Dockerfile
        share.py                 # der eigentliche Dienst (stdlib-only)
        run.sh                   # NICHT mehr benutzt (s. Fix unten), kann bleiben/weg
        README.md

### Verhalten von `share.py`
- Python-**Standardbibliothek only**, kein pip/Fremdpaket.
- Lauscht intern per HTTP auf **Port 8099** (Ingress-Port).
- **Ingress-tauglich:** liest den Basispfad aus dem Header `X-Ingress-Path` und
  setzt ihn ins HTML (`const BASE`), damit die fetch()-Aufrufe unter HAs
  wechselndem Unterpfad ankommen. Routen per `endswith`:
  - `GET  …/`      → HTML-Seite (mit eingesetztem BASE)
  - `GET  …/get`   → aktuelles Geheimnis (Klartext)
  - `POST …/set`   → Geheimnis ablegen
  - `POST …/clear` → Geheimnis löschen
- Geheimnis lebt in einem Dict **nur im RAM**; `log_message` überschrieben →
  keine Inhalte im Add-on-Log.

## Letzter Fehler & angewandter Fix (WICHTIG)

**Installation schlug beim Docker-Build fehl:**

    ERROR: failed to solve: base name (${BUILD_FROM}) should not be blank

Ursache: Das ursprüngliche Dockerfile nutzte `ARG BUILD_FROM` / `FROM
${BUILD_FROM}`. Der Supervisor 2026.09 befüllt `BUILD_FROM` **nicht**
automatisch (es fehlte eine `build.yaml`) → leeres Basis-Image → Build bricht ab.

**Fix (in den Repo-Dateien schon umgesetzt, aber noch NICHT von Adrian gepusht/gebaut):**
- `Dockerfile` auf **festes öffentliches Basis-Image** umgestellt → `BUILD_FROM`
  entfällt, Build ist deterministisch. `run.sh`/bashio dadurch überflüssig.
- `config.yaml` **Version auf 1.0.1** hochgezählt (erzwingt echten Neubau statt
  Cache des kaputten Images).

Aktuelles Dockerfile:

    FROM python:3-alpine
    COPY share.py /
    CMD [ "python3", "/share.py" ]

## NÄCHSTE SCHRITTE (offen, hier weitermachen)

1. Geänderte Dateien ins Repo pushen (`Dockerfile`, `config.yaml` mit 1.0.1).
2. In HA: Einstellungen → Apps → App Store → Menü → **Neu laden**, dann Add-on
   **neu bauen/installieren** (bei kaputtem Alt-Zustand: deinstallieren + neu).
3. **End-to-end testen:** auf Gerät A ablegen, auf Gerät B anzeigen.
4. Prüfen: erscheint der Sidebar-Eintrag (Ingress-Panel), greift der HA-Login davor.

## Wichtige Entscheidungen & Trade-offs (bitte nicht versehentlich rückgängig machen)

- **Ingress statt offenem Port:** UI läuft eingebettet in HA, hinter HA-Login →
  Zugangsschutz gratis, und es testet die eigentliche HA-Mechanik. Ein Port-Mapping
  würde das umgehen.
- **TLS ist Sache von HA**, nicht des Add-ons. (Der Kopieren-Button im Browser
  braucht einen sicheren Kontext → funktioniert nur, wenn **HA selbst über HTTPS**
  aufgerufen wird. Auf der Demo-VM per http bleibt er stumm – kein Bug.)
- **`python:3-alpine` statt HA-Basis-Image:** bewusst gewählt für
  deterministischen Build. Preis: HA vergibt evtl. eine niedrigere
  „Sicherheitsbewertung", kein `bashio`/s6. Der **idiomatische HA-Weg**
  (HA-Basis-Image + `build.yaml` mit passendem Tag + `bashio`) ist **bewusst
  aufgeschoben** für ein späteres „echtes" Add-on.
- **Spurlosigkeit:** Geheimnis nur im RAM, keine Logs. Beim Add-on-Neustart weg.
- Es existiert außerdem eine **Standalone-Variante** von `share.py` (mit TLS +
  selbstsigniertem Zertifikat, Port 8443) für den Nicht-HA-Betrieb – separat,
  nicht Teil des Add-ons.

## Weitere offene Fäden (optional / später)

- **Hardware:** N100-Mini-PC (freies Linux/Docker drunter → maximale Flexibilität,
  HA als eine von mehreren Sachen) vs. HA Green (Appliance, nur HA-OS-Welt).
  Die spürbare Build-Reibung im Add-on-System ist ein Datenpunkt pro freiem Linux.
- **Gegenprobe Portainer:** dasselbe Skript als freier Docker-Container laufen
  lassen – testet die andere Achse („Docker neben HA" statt HA-Add-on-Modell).
- **Feature-Ideen:** „burn after reading"/Ablauf; optionaler Zugangs-Token
  (nur nötig, falls nicht über Ingress betrieben).

## Kommunikationsstil (für konsistente Weiterarbeit)

Deutsch, dicht und direkt, ehrliche Trade-off-Analyse statt Best-Practice-Predigt,
Fachbegriffe nur wo nötig und dann kurz erklärt.
