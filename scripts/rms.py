# Mede o volume do audio.wav a cada 10 ms (db.npy). Com tempos como argumento, mostra o perfil em volta de cada um.
import numpy as np, wave, sys
w=wave.open('audio.wav'); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(float)/32768
hop=160; n=len(a)//hop; e=np.sqrt((a[:n*hop].reshape(n,hop)**2).mean(1)+1e-12); db=20*np.log10(e)
np.save('db.npy',db)
for t in map(float,sys.argv[1:]):
    i0=int((t-0.8)*100); row=db[i0:i0+160]
    print(f"{t:7.2f}: "+''.join('#' if v>-35 else ('+' if v>-45 else ('.' if v>-55 else ' ')) for v in row))
