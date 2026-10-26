# Lê trechos.json ([[inicio,fim],...] em segundos do bruto), acha o início/fim exato pelo volume,
# monta fala.mp4 em 1,1x e transcreve a fala montada palavra por palavra (palavras.json + legendas.json).
import numpy as np, subprocess, json, glob, re, os
_m=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','modelos','ggml-large-v3-turbo.bin')
MOD=os.environ.get('WHISPER_MODELO') or (_m if os.path.exists(_m) else os.path.expanduser('~/transcrever/modelos/ggml-large-v3-turbo.bin'))
VEL=1.1
db=np.load('db.npy'); B=sorted(glob.glob('bruto.*'))[0]
SEG=json.load(open('trechos.json'))
def onset(s):
    for i in range(max(int((s-0.35)*100),0), int((s+0.7)*100)):
        if (db[i:i+5]>-45).all() and (i<20 or db[max(i-20,0):i].max()<-44): return max(i/100-0.07,0)
    return s
def fim(e):
    for j in range(int((e-0.3)*100), int((e+0.8)*100)):
        if (db[j:j+15]<-50).all(): return j/100+0.10
    return e+0.1
parts=[]
for k,(s,e) in enumerate(SEG):
    a,b=onset(s),fim(e); print(f"{s:7.2f}-{e:7.2f} -> {a:7.2f}-{b:7.2f}")
    f=f'seg{k:02d}.mp4'; parts.append(f)
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(a),'-to',str(b),'-i',B,
      '-vf',f'setpts=(PTS-STARTPTS)/{VEL},fps=30','-af',f'atempo={VEL},afade=t=in:d=0.02,areverse,afade=t=in:d=0.04,areverse',
      '-c:v','libx264','-crf','16','-preset','fast','-c:a','aac','-ar','48000','-b:a','256k',f],check=True)
open('lista.txt','w').write(''.join(f"file '{p}'\n" for p in parts))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-i','lista.txt','-c','copy','fala.mp4'],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i','fala.mp4','-ar','16000','-ac','1','fala.wav'],check=True)
subprocess.run(['whisper-cli','-m',MOD,'-l','pt','-f','fala.wav','-ml','1','-sow','-osrt','-of','palavras','-t','8'],capture_output=True,check=True)
f=lambda x:int(x[:2])*3600+int(x[3:5])*60+float(x[6:].replace(',','.'))
ws=[(f(a),f(c),w.strip()) for a,c,w in re.findall(r'\d+\n(\S+) --> (\S+)\n(.*?)\n(?:\n|$)',open('palavras.srt').read()+'\n') if w.strip()]
json.dump(ws,open('palavras.json','w'),ensure_ascii=False)
# legenda em frases curtas (quebra em ponto/interrogação, vírgula com 12+ letras, ou 24+ letras)
rep={'black':'BLACK'}; ch=[];cur=[]
for i,w in enumerate(ws):
    w=[w[0],w[1],rep.get(w[2],w[2])]; cur.append(w); txt=' '.join(x[2] for x in cur); nxt=ws[i+1] if i+1<len(ws) else None
    if w[2][-1] in '.?' or (w[2][-1]==',' and len(txt)>=12) or len(txt)>=24 or nxt is None or nxt[0]-w[1]>0.5:
        ch.append([cur[0][0],cur[-1][1],txt]); cur=[]
for k in range(len(ch)): ch[k][1]=min(ch[k+1][0] if k+1<len(ch) else ch[k][1]+0.6, ch[k][1]+0.5)
json.dump(ch,open('legendas.json','w'),ensure_ascii=False)
print('duração:',subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0','fala.mp4'],capture_output=True,text=True).stdout.strip())
print(' '.join(f"{w}[{a:.1f}]" for a,b,w in ws))
