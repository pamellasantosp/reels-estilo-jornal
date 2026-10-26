---
name: reels-estilo-jornal
description: Edita Reels no estilo "jornal/colagem" aprovado pela Pâmella (papel bege, tarjas recortadas, fotos P&B fatiadas, números gigantes, documento com marca-texto, tela dividida gráfico/expert, rabiscos vermelhos). Use quando ela pedir "edita no estilo jornal", "no modelo do Safra", "igual aquele vídeo de jornal", "estilo colagem/notícia", ou mandar um bruto de expert falando de caso/notícia para virar Reels nesse estilo.
---

# Reels estilo jornal

Esta skill transforma um bruto de expert falando para a câmera em um Reels no estilo jornal/colagem. O exemplo aprovado em 26/10/2026 é o "V1 - Safra", da Giovana, com 87 s. Ele está no Drive em Vídeos Pâmella > Modelos de edição > Estilo jornal.

Tudo fica nesta pasta: `scripts/`, `assets/` (fontes, papel e sons) e `exemplo/` (o roteiro do Safra).
`S` = `~/.claude/skills/reels-estilo-jornal`.

**Instalação (uma vez por Mac):** rode `$S/instalar.sh`. Ele instala via Homebrew o `ffmpeg`, o `whisper-cpp` e o Python 3.12. Cria `$S/.venv` com numpy e Playwright/Chromium e baixa o modelo de transcrição para `$S/modelos/` (1,6 GB). Se `$S/.venv` não existir, rode o instalador antes de qualquer passo. Os scripts acham os caminhos sozinhos (`scripts/_env.sh`). 

## Fluxo (cerca de 30 min, sendo 15 de render)

1. **Pasta de trabalho no scratchpad** (nunca em pasta do Mac). Copie o bruto para lá como `bruto.mov`. Arquivos grandes do Drive: copie com `cp`, não leia direto.
2. `$S/scripts/preparar.sh <pasta>` gera:
   - `audio.wav`
   - `db.npy` (volume a cada 10 ms)
   - `tr.srt` (transcrição do bruto)
3. **Escolha dos trechos** → `trechos.json` = `[[inicio,fim],...]`, em segundos do bruto, a partir do `tr.srt`.
   - Mire em 45–90 s. O primeiro trecho é o gancho do caso (nome + fato forte). Depois vem a virada e a lição. O fim é o CTA.
   - Tire erros de gravação, contagens "3, 2, 1", conversas com a equipe e frases repetidas. Fique com a última tomada.
   - Os tempos do whisper no bruto inteiro são aproximados. O `cortar.py` refina pelo volume (início a -45 dB, fim a -50 dB). Para conferir uma emenda, use `$S/.venv/bin/python $S/scripts/rms.py <t1> <t2>...` dentro da pasta.
4. Dentro da pasta, rode `$S/.venv/bin/python $S/scripts/cortar.py`. Ele gera:
   - `fala.mp4` (fala em 1,1x)
   - `palavras.json` (tempo de cada palavra na fala montada)
   - `legendas.json`

   Leia a lista `palavra[tempo]` que ele imprime. É a base do roteiro.
5. **Roteiro visual** → `cenas.js`. Copie `$S/exemplo/cenas.js` e reescreva seguindo as regras abaixo. As fotos vão em `<pasta>/img/`.
6. `$S/scripts/montar.sh <pasta> prova` gera `previa.jpg`, com um quadro por cena composto sobre o vídeo. Abra com Read e confira se:
   - algum texto está cortado,
   - algum elemento sobrepõe outro,
   - algum elemento cobre o rosto,
   - a legenda está legível.
7. `$S/scripts/montar.sh <pasta>` gera `final.mp4` (com capa embutida) e `capa.jpg`.
   - Leva uns 15 min para 90 s. Rode com `run_in_background`.
   - Os `ov_*.mov` temporários ocupam cerca de 3 GB, e o disco vive cheio. O script apaga esses arquivos no fim.
8. Gere uma grade de conferência do final: `ffmpeg -i final.mp4 -vf "fps=1/4,scale=200:-1,tile=11x2" -frames:v 1 conf.jpg`. Depois salve `final.mp4` e `capa.jpg` no Drive do cliente e feche com o link.

Se a pessoa estiver enquadrada diferente da Giovana, defina `ROSTO_Y=<altura do rosto no bruto 1080x1920>` antes do `montar.sh`. O padrão é 760.

## Roteiro: como escrever `cenas.js`

```js
window.CENAS = [ {a:<início em s na fala.mp4>, L:'S'|'D'|'G', it:[ ...itens ]}, ... ];
window.FIM = <duração da fala.mp4>;
```

Cada cena vai do seu `a` até o `a` da próxima.

**Layouts:**
- `S`: ela em tela cheia. O zoom alterna 1,0 / 1,12 entre as cenas S.
- `D`: gráfico em cima (y 0–960) e ela embaixo.
- `G`: gráfico em tela cheia (y 0–1920).

**Itens:** o `t` é o tempo de entrada, igual ao início da palavra em `palavras.json`. `x` é a posição em px ou `'c'` para centralizar. `y` é o topo do elemento, em px.

| k | campos | o que é |
|---|---|---|
| `bg` | txt, y, s, d | palavra gigante cinza ao fundo (Anton), desliza; `d:1` inverte o sentido |
| `tarja` | t, txt, x, y, s, f (`serif`/`cond`), inv (1 = fundo preto), r (graus), snd | tarja recortada, entra como carimbo; som de clique |
| `big` | t, txt, x, y, s, f | número ou palavra gigante sem fundo; som de impacto |
| `kick` | t, txt, x, y, s, f (`serif`/`cond`/`mono`), cor | texto pequeno de apoio, sem som |
| `foto` | t, src, x, y, w, h, r, pos (background-position) | foto P&B com borda, entra em 4 faixas; clique |
| `line` | t, tipo (`under`/`strike`/`check`/`circle`), x, y, w, h | rabisco vermelho desenhado à mão |
| `stamp` | t, txt, x, y, r | carimbo vermelho com borda; impacto |
| `doc` | t, cab, tit, rod, pag, txt, ti, tf | folha de documento com marca-texto amarelo de `ti` a `tf` |

`snd:'imp'` ou `snd:'clk'` força o som de um item.

## Regras de direção (o que fez o Safra funcionar)

- **Uma cena por frase**, trocando a cada 2–7 s. Alterne D → G → S sem repetir o mesmo layout mais de 2 vezes seguidas.
- **D** para fatos com foto ou tarja (nome de pessoa, lugar, empresa). **G** para números e conceitos fortes ("2023", "3 PAÍSES", "SEM CLAREZA"). **S** para frases de opinião, curtas, e para o CTA.
- **Toda tarja entra na palavra exata** em que ela fala. Use o tempo de `palavras.json`, nunca uma estimativa.
- Textos das tarjas: as palavras dela, em caixa alta, curtas (até cerca de 26 letras por linha). Alterne serif e cond, claro e escuro, com rotação de -2° a 2°.
- Tamanhos que funcionaram:
  - tarja principal: s 84–110
  - tarja de apoio: s 46–64
  - número gigante: s 250–560
  - bg: s 250–380
  - kick: s 40–52
- Em D, tudo cabe em y < 900. Em S, as tarjas ficam acima da cabeça (y < 470) e **nunca cobrem o rosto**.
- **Documento:** nunca inventar trecho de documento real. Use a fala dela e a etiqueta "Resumo do caso".
- **Fotos:** busque no Wikimedia Commons, só domínio público ou CC. Use a API `commons.wikimedia.org/w/api.php?action=query&list=search&srnamespace=6`, depois `prop=imageinfo&iiprop=url|extmetadata` para ver a licença. Baixe com User-Agent. Recorte a pessoa com ffmpeg `crop`. Sem foto livre da pessoa, use só tarja com o nome.
- Lugar ou instituição: foto do prédio, da cidade ou do tribunal + tarja com o nome.
- CTA: tarja "COMENTE" + a palavra-chave gigante em tarja escura, acima da cabeça.
- Mensagens oficiais: "Giovana", nunca "Gi".

## Ajustes já aprovados (não mudar sem ela pedir)

- **Visual:** papel bege, tinta #151412, vermelho #b3261e, marca-texto #e9c64b. Clarão de 0,16 s na entrada das cenas D e G.
- **Legenda:** Montserrat Bold 44 em frases curtas. Branca com sombra sobre o vídeo, escura sobre o papel (G). Fica em y 1250 (S), 1560 (D) e 1680 (G).
- **Som:** fala em 1,1x, sem música. Impacto nos números grandes e clique nas tarjas e fotos. Volume normalizado em -14 LUFS.
- **Capa:** quadro de 0,9 s embutido como attached_pic, para a prévia do WhatsApp.
