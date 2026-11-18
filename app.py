#!/usr/bin/env python3
"""Servidor local do painel escolar.

Uso:
    python app.py           -> modo real (usa scraper.py)
    python app.py --demo    -> testa tudo sem acessar a Sala do Futuro

Escuta só em 127.0.0.1: nada fica acessível para outros aparelhos.
A senha fica apenas na memória enquanto o programa estiver aberto.
"""
import json
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import scraper

BASE = Path(__file__).parent
DADOS = BASE / "dados"
DADOS.mkdir(exist_ok=True)
DEMO = "--demo" in sys.argv
PORTA = 8765
SESSAO = {}  # credenciais só em memória


def ler(nome, padrao):
    try:
        return json.loads((DADOS / nome).read_text(encoding="utf-8"))
    except Exception:
        return padrao


def gravar(nome, obj):
    (DADOS / nome).write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, code, obj):
        b = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def _local(self):
        return self.headers.get("Host", "").split(":")[0] in ("127.0.0.1", "localhost")

    def do_GET(self):
        if not self._local():
            return self._json(403, {"erro": "Acesso negado"})
        if self.path in ("/", "/index.html"):
            b = (BASE / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
        elif self.path == "/api/ping":
            self._json(200, {"ok": True, "demo": DEMO})
        elif self.path == "/api/lembretes":
            self._json(200, ler("lembretes.json", []))
        elif self.path == "/api/perfil":
            self._json(200, ler("perfil.json", {}))
        else:
            self._json(404, {"erro": "Não encontrado"})

    def do_POST(self):
        if not self._local() or self.headers.get("X-Painel") != "1":
            return self._json(403, {"erro": "Acesso negado"})
        try:
            n = int(self.headers.get("Content-Length") or 0)
            corpo = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return self._json(400, {"erro": "Pedido inválido"})

        if self.path == "/api/lembretes" and isinstance(corpo, list):
            gravar("lembretes.json", corpo)
            return self._json(200, {"ok": True})
        if self.path == "/api/perfil" and isinstance(corpo, dict):
            gravar("perfil.json", corpo)
            return self._json(200, {"ok": True})

        if self.path in ("/api/login", "/api/sync"):
            if self.path == "/api/login":
                ra, dg, senha = corpo.get("ra", ""), str(corpo.get("dg", "")), corpo.get("senha", "")
                if not (ra.isdigit() and len(ra) == 9 and len(dg) == 1 and senha):
                    return self._json(400, {"erro": "RA, dígito ou senha inválidos"})
                SESSAO["cred"] = (ra, dg, senha)
            if "cred" not in SESSAO:
                return self._json(401, {"erro": "Entre de novo com RA e senha"})
            try:
                dados = {} if DEMO else scraper.buscar(*SESSAO["cred"])
                return self._json(200, dados)
            except scraper.ErroLogin as e:
                SESSAO.pop("cred", None)
                return self._json(401, {"erro": str(e)})
            except Exception as e:
                return self._json(500, {"erro": f"Não consegui ler a Sala do Futuro: {e}"})
        self._json(404, {"erro": "Não encontrado"})


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("127.0.0.1", PORTA), H)
    url = f"http://127.0.0.1:{PORTA}/"
    print(("MODO DEMO. " if DEMO else "") + f"Painel aberto em {url}  (Ctrl+C para fechar)")
    webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nFechado.")
