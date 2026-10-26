#!/bin/zsh
# Uso: montar.sh <pasta-de-trabalho> [prova]
#  prova  -> só gera previa.jpg (quadros de amostra compostos) para conferir antes do render completo
set -e
M=${0:A:h}; source $M/_env.sh; W=${1:A}; cd $W
cp $M/index.html $M/render.py .
$PW render.py stills 0.5 >/dev/null   # gera info.json (cenas e sons)
$PY $M/base.py
if [[ $2 == prova ]]; then
  T=($($PY -c "import json;c=json.load(open('info.json'))['cenas'];print(' '.join(f'{(a+b)/2+0.3:.2f}' for a,b,L in c))"))
  $PW render.py stills $T; args=()
  for t in $T; do ffmpeg -v error -y -ss $t -i base.mp4 -i st_$t.png -filter_complex "[0][1]overlay,scale=270:480" -frames:v 1 c_$t.png; args+=(-i c_$t.png); done
  (( ${#T} % 2 )) && args+=(-i c_${T[-1]}.png) && T+=(${T[-1]})
  ffmpeg -v error -y $args -filter_complex "xstack=inputs=${#T}:grid=$(( (${#T}+1)/2 ))x2:fill=black" previa.jpg; rm -f st_*.png c_*.png; echo "previa.jpg"; exit 0
fi
N=$($PY -c "import json;print(int(json.load(open('info.json'))['cenas'][-1][1]*30))"); K=6
for k in $(seq 0 $((K-1))); do $PW render.py faixa $k $((N*k/K)) $((N*(k+1)/K)) & done; wait
$PY $M/sons.py
printf "file 'ov_%d.mov'\n" $(seq 0 $((K-1))) > ovl.txt
ffmpeg -v error -y -i base.mp4 -f concat -i ovl.txt -i audio_final.wav -filter_complex "[0:v][1:v]overlay=shortest=0,format=yuv420p[v];[2:a]loudnorm=I=-14:TP=-1.5[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -crf 18 -preset medium -profile:v high -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest final_sem_capa.mp4
ffmpeg -v error -y -ss 0.9 -i final_sem_capa.mp4 -frames:v 1 capa.jpg
ffmpeg -v error -y -i final_sem_capa.mp4 -i capa.jpg -map 0 -map 1 -c copy -disposition:v:1 attached_pic final.mp4
rm -f ov_*.mov final_sem_capa.mp4 st_*.png
echo "Pronto: $W/final.mp4 + capa.jpg"
