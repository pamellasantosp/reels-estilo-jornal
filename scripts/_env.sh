# Caminhos usados por todos os scripts. Prioridade: variável de ambiente > instalação da skill > Mac da Pâmella.
S=${0:A:h:h}
PY=${JORNAL_PY:-$S/.venv/bin/python}; [[ -x $PY ]] || PY=~/reels/venv/bin/python
PW=${JORNAL_PW:-$S/.venv/bin/python}; [[ -x $PW ]] || PW=~/transcrever/.venv/bin/python
export WHISPER_MODELO=${WHISPER_MODELO:-$S/modelos/ggml-large-v3-turbo.bin}
[[ -f $WHISPER_MODELO ]] || export WHISPER_MODELO=~/transcrever/modelos/ggml-large-v3-turbo.bin
