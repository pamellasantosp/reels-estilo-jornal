#!/bin/zsh
# Instala tudo o que a skill precisa (Mac). Rodar uma vez: ~/.claude/skills/reels-estilo-jornal/instalar.sh
set -e
S=${0:A:h}; cd $S
command -v brew >/dev/null || { echo "Instale o Homebrew primeiro: https://brew.sh"; exit 1; }
for p in ffmpeg whisper-cpp python@3.12; do brew list $p >/dev/null 2>&1 || brew install $p; done
[[ -x .venv/bin/python ]] || $(brew --prefix)/bin/python3.12 -m venv .venv
.venv/bin/pip install -q numpy playwright && .venv/bin/python -m playwright install chromium
mkdir -p modelos
[[ -f modelos/ggml-large-v3-turbo.bin ]] || curl -L -o modelos/ggml-large-v3-turbo.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin
echo "Pronto. A skill reels-estilo-jornal está instalada."
