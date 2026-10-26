import json, subprocess
I=json.load(open('info.json')); import os; E=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','assets','sons')+'/'
ins=['-i','fala.mp4','-i',E+'impacto-titulo.wav','-i',E+'clique-mouse.wav']
s=I['sons']; ni=sum(1 for t,k in s if k=='imp'); nc=len(s)-ni
fc=f"[1:a]volume=0.55,asplit={ni}" + ''.join(f'[i{j}]' for j in range(ni))+f";[2:a]volume=0.35,asplit={nc}"+''.join(f'[c{j}]' for j in range(nc))+';'
mix=[];a=b=0
for t,k in s:
    if k=='imp': d=max(int((t-0.26)*1000),0); fc+=f"[i{a}]adelay={d}|{d}[x{len(mix)}];"; a+=1
    else: d=int(t*1000); fc+=f"[c{b}]adelay={d}|{d}[x{len(mix)}];"; b+=1
    mix.append(f'[x{len(mix)}]')
fc+="[0:a]"+''.join(mix)+f"amix=inputs={len(mix)+1}:normalize=0,alimiter=limit=0.95[a]"
subprocess.run(['ffmpeg','-v','error','-y',*ins,'-filter_complex',fc,'-map','[a]','-c:a','pcm_s16le','audio_final.wav'],check=True)
