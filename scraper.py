#!/usr/bin/env python3
"""Leitura da Sala do Futuro.

PASSO 1 (explorar): python scraper.py --explorar
  Abre um navegador. VOCÊ faz o login normalmente e visita Tarefas, Notas e
  Horário. O programa só guarda as respostas JSON das telas em capturas/.
  Sua senha nunca passa por este programa nesse modo.

PASSO 2: com as capturas, o interpretar() abaixo é ajustado para o formato real.

Formato que buscar() deve devolver (todas as chaves são opcionais):
  {
    "tarefas": [{"t": "Redação: tema", "m": "Português", "tipo": "Redação",
                 "due": "2026-11-20", "ok": false}],      # tipo: Prova, Redação,
                                                           # Pesquisa, Trabalho, Exercício
    "notas":   [["Matemática", [6.5, 7, 5.5, null], 6]],   # [matéria, [4 bimestres], faltas]
    "horario": {"1": ["Matemática", "..."]},               # dia da semana (1=segunda) -> 6 aulas
    "salas":   {"Matemática": "Sala 12"}
  }
"""
import json
import sys
from pathlib import Path

URL_LOGIN = "https://saladofuturo.educacao.sp.gov.br/"
CAPTURAS = Path(__file__).parent / "capturas"

# AJUSTAR depois da exploração: seletores dos campos da tela de login.
SELETORES = {
    "ra": "input[name='ra']",
    "digito": "input[name='digito']",
    "senha": "input[type='password']",
    "entrar": "button[type='submit']",
}


class ErroLogin(Exception):
    pass


def explorar():
    from playwright.sync_api import sync_playwright

    CAPTURAS.mkdir(exist_ok=True)
    n = [0]

    def ao_responder(r):
        try:
            if "json" in (r.headers.get("content-type") or ""):
                n[0] += 1
                arq = CAPTURAS / f"{n[0]:03d}.json"
                arq.write_text(
                    json.dumps(
                        {"url": r.url.split("?")[0], "status": r.status, "corpo": r.json()},
                        ensure_ascii=False, indent=1,
                    ),
                    encoding="utf-8",
                )
        except Exception:
            pass

    with sync_playwright() as p:
        nav = p.chromium.launch(headless=False)
        pg = nav.new_page()
        pg.on("response", ao_responder)
        pg.goto(URL_LOGIN)
        input("Faça login, abra Tarefas, Notas e Horário. Depois volte aqui e aperte Enter... ")
        nav.close()
    print(f"{n[0]} respostas salvas em {CAPTURAS}. Revise e apague dados pessoais antes de compartilhar.")


def interpretar(respostas):
    """Transforma as respostas capturadas no formato do painel. A ajustar."""
    raise NotImplementedError(
        "O leitor ainda não conhece o formato da Sala do Futuro. "
        "Rode `python scraper.py --explorar` e envie as capturas (sem dados pessoais) para ajustarmos."
    )


def buscar(ra, dg, senha):
    from playwright.sync_api import sync_playwright

    respostas = []
    with sync_playwright() as p:
        nav = p.chromium.launch(headless=True)
        pg = nav.new_page()

        def ao_responder(r):
            try:
                if "json" in (r.headers.get("content-type") or ""):
                    respostas.append({"url": r.url.split("?")[0], "corpo": r.json()})
            except Exception:
                pass

        pg.on("response", ao_responder)
        pg.goto(URL_LOGIN)
        pg.fill(SELETORES["ra"], ra)
        pg.fill(SELETORES["digito"], dg)
        pg.fill(SELETORES["senha"], senha)
        pg.click(SELETORES["entrar"])
        pg.wait_for_load_state("networkidle")
        # AJUSTAR: navegar até as telas de tarefas, notas e horário.
        nav.close()
    return interpretar(respostas)


if __name__ == "__main__":
    if "--explorar" in sys.argv:
        explorar()
    else:
        print(__doc__)
