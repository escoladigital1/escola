# Meu painel escolar (versão local)

Painel com aulas, tarefas (provas, redações, pesquisas), lembretes, notas e perfil.
Roda só no seu computador. Nada vai para a internet além do login na Sala do Futuro.

## 1. Instalar (uma vez)

1. Instale o Python 3.10 ou mais novo: https://www.python.org/downloads/ (no Windows, marque "Add Python to PATH").
2. Abra o terminal (Windows: Prompt de Comando) dentro desta pasta e rode:

```
pip install playwright
playwright install chromium
```

## 2. Testar o painel (sem acessar a escola)

```
python app.py --demo
```

O navegador abre sozinho. Use qualquer RA de teste. Dá para criar lembretes e editar o perfil; eles ficam salvos na pasta `dados/`.

## 3. Conectar na Sala do Futuro

A Sala do Futuro não tem API pública, então o leitor precisa ser ajustado ao formato real das telas. Isso é feito em duas etapas:

1. Rode `python scraper.py --explorar`. Abre um navegador: **você** faz login normalmente e abre Tarefas, Notas e Horário. A senha não passa pelo programa.
2. As respostas ficam na pasta `capturas/`. **Abra os arquivos, apague nome, RA, CPF, e-mail e qualquer código de acesso (token)** e me envie o conteúdo. Com isso eu ajusto o `interpretar()` do `scraper.py`.

Depois disso: `python app.py` (sem `--demo`).

## Segurança

- O servidor só aceita acessos do próprio computador (127.0.0.1).
- A senha fica só na memória enquanto o programa estiver aberto. Não é gravada.
- `dados/` e `capturas/` ficam no seu computador. Não compartilhe sem revisar.
- Se a escola exigir confirmação extra no login (captcha, código), o login automático pode não funcionar. Me avise.
