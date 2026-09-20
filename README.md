# Secret Share (Home-Assistant-Add-on)

Winziger Dienst zum kurzlebigen Teilen von Text/Passwoertern zwischen deinen
Geraeten im LAN. Ein Geraet legt Text ab, ein anderes holt ihn. Der Inhalt
lebt nur im Arbeitsspeicher und ist beim Neustart des Add-ons weg.

Zweck hier: ein bewusst simples erstes Add-on, um HAs Add-on- und
Ingress-Mechanik auszuprobieren.

## Installieren

1. Repo auf GitHub anlegen und diese Dateien so hochladen, dass die Struktur
   erhalten bleibt:

       repo-wurzel/
         repository.yaml
         secret_share/
           config.yaml
           Dockerfile
           run.sh
           share.py
           README.md

2. In HA: Einstellungen -> Add-ons -> Add-on-Store -> Menue (oben rechts, drei
   Punkte) -> Repositories -> die URL deines GitHub-Repos eintragen.

3. Kurz warten, dann taucht "Secret Share" im Store auf. Installieren.

4. Starten. Wegen `boot: auto` startet HA es ab jetzt nach jedem Neustart selbst.

5. In der HA-Seitenleiste erscheint der Eintrag (Schluessel-Symbol). Anklicken
   -> die Oberflaeche laeuft eingebettet in HA, hinter dem HA-Login.

## Gut zu wissen

- **Zugang**: Nur wer in HA eingeloggt ist, kommt an die Seite (uebernimmt der
  Ingress-Proxy). Kein extra Passwort noetig.
- **Kopieren-Button**: Funktioniert nur, wenn du HA selbst ueber HTTPS
  aufrufst (der Browser gibt die Zwischenablage sonst nicht frei). Sonst Text
  von Hand markieren.
- **Spurlos**: Der geteilte Text steht nie auf der Platte und nie im
  Add-on-Protokoll. Add-on neu starten = Inhalt weg.
- **Falls der Build ueber BUILD_FROM meckert**: eine `build.yaml` neben das
  Dockerfile legen, die je Prozessor-Typ das Basis-Image benennt. In den
  meisten Setups ist das aber nicht noetig.
