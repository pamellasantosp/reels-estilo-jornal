#!/bin/zsh
# Uso: preparar.sh <pasta-de-trabalho>   (a pasta precisa ter bruto.mov ou bruto.mp4)
set -e
M=${0:A:h}; source $M/_env.sh; W=${1:A}; cd $W
B=$(ls bruto.* | head -1)
ln -sfn $M/../assets/fontes fontes; mkdir -p img; cp -n $M/../assets/img/papel.jpg img/ 2>/dev/null || true; cp $M/index.html $M/render.py .
ffmpeg -v error -y -i $B -ar 16000 -ac 1 audio.wav
$PY $M/rms.py
whisper-cli -m $WHISPER_MODELO -l pt -f audio.wav -osrt -of tr -t 8 >/dev/null 2>&1
echo "Python para os próximos passos: $PY"
echo "Pronto: tr.srt (transcrição do bruto). Agora escreva trechos.json e rode cortar.py"
