import json, subprocess, os
# ROSTO_Y = altura do rosto no bruto 1080x1920 (padrão 760, enquadramento da Giovana no Safra)
RY=int(os.environ.get('ROSTO_Y',760))
I=json.load(open('info.json'))
z=[];d=[];n=0
for a,b,L in I['cenas']:
    if L=='S':
        if n%2: z.append((a,b))
        n+=1
    if L=='D': d.append((a,b))
ex=lambda r:'+'.join(f'between(t,{a},{b-0.001})' for a,b in r) or '0'
fc=(f"[0:v]split=3[a][b][c];[b]scale=1210:2150,crop=1080:1920:65:{round(RY*0.12)}[z];"
    f"[c]crop=1080:960:0:{min(max(RY-380,0),960)},pad=1080:1920:0:960[d];[a][z]overlay=enable='{ex(z)}'[az];[az][d]overlay=enable='{ex(d)}',format=yuv420p[v]")
subprocess.run(['ffmpeg','-v','error','-y','-i','fala.mp4','-filter_complex',fc,'-map','[v]','-an','-c:v','libx264','-crf','15','-preset','fast','base.mp4'],check=True)
