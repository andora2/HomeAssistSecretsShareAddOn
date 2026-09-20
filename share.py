#!/usr/bin/env python3
"""
Secret Share als Home-Assistant-Ingress-Add-on. Nur Python-Standardbibliothek.

Unterschied zur Standalone-Version:
- Laeuft intern per HTTP auf Port 8099 (TLS macht HA aussen herum).
- Ingress-tauglich: HA serviert die App unter einem wechselnden Unterpfad.
  Damit die fetch()-Aufrufe dort ankommen, wird der Basispfad aus dem
  Header 'X-Ingress-Path' gelesen und ins HTML eingesetzt.
Der geteilte Text lebt weiterhin ausschliesslich im RAM und ist beim
Neustart des Add-ons weg.
"""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 8099
secret = {"text": ""}          # lebt ausschliesslich im Arbeitsspeicher

PAGE = """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Secret Share</title>
<style>
  body { font-family: system-ui, sans-serif; max-width: 40rem; margin: 1rem auto; padding: 0 1rem; }
  textarea { width: 100%; height: 6rem; font-size: 1rem; box-sizing: border-box; }
  button { font-size: 1rem; padding: .6rem 1rem; margin: .4rem .4rem 0 0; }
  #out { white-space: pre-wrap; word-break: break-all; background: #f2f2f2;
         padding: 1rem; border-radius: .5rem; min-height: 1.5rem; }
  h2 { margin-top: 2rem; }
</style>
</head>
<body>
<h1>Secret Share</h1>

<h2>Ablegen</h2>
<textarea id="in" placeholder="Passwort o.ae."></textarea><br>
<button onclick="save()">Ablegen</button>

<h2>Abholen</h2>
<div id="out"></div>
<button onclick="load()">Anzeigen</button>
<button onclick="copyOut()">Kopieren</button>
<button onclick="clr()">Loeschen</button>

<script>
// Basispfad, den HAs Ingress vorgibt. Leer, wenn ohne Ingress betrieben.
const BASE = "__BASE__";
async function save(){
  const t = document.getElementById('in').value;
  await fetch(BASE + '/set', {method:'POST', body:t});
  document.getElementById('in').value = '';
  alert('Abgelegt.');
}
async function load(){
  const r = await fetch(BASE + '/get');
  document.getElementById('out').textContent = await r.text();
}
async function clr(){
  await fetch(BASE + '/clear', {method:'POST'});
  document.getElementById('out').textContent = '';
}
async function copyOut(){
  const t = document.getElementById('out').textContent;
  try { await navigator.clipboard.writeText(t); alert('Kopiert.'); }
  catch(e){ alert('Kopieren geht nur, wenn HA selbst ueber HTTPS laeuft. Bitte manuell markieren.'); }
}
</script>
</body>
</html>
"""


class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="text/plain; charset=utf-8"):
        b = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        # Endet der Pfad auf /get -> Geheimnis zurueckgeben, sonst die Seite.
        # (Unter Ingress hat der Pfad einen Praefix, daher endswith statt ==.)
        if self.path.endswith("/get"):
            self._send(200, secret["text"])
        else:
            base = self.headers.get("X-Ingress-Path", "")
            self._send(200, PAGE.replace("__BASE__", base), "text/html; charset=utf-8")

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(n).decode()
        if self.path.endswith("/set"):
            secret["text"] = data
            self._send(200, "ok")
        elif self.path.endswith("/clear"):
            secret["text"] = ""
            self._send(200, "ok")
        else:
            self._send(404, "not found")

    def log_message(self, *args):   # keine Logs -> keine Inhalte im Add-on-Protokoll
        pass


if __name__ == "__main__":
    print(f"Secret Share laeuft auf :{PORT} (Ingress)")
    ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
