import sys, json, subprocess, asyncio
from playwright.async_api import async_playwright
BASE='file://'+__import__('os').path.abspath('index.html')
LEGS=json.load(open('legendas.json'))
FPS=30
async def pagina(pw):
    b=await pw.chromium.launch(); pg=await b.new_page(viewport={'width':1080,'height':1920})
    await pg.goto(BASE); await pg.evaluate('document.fonts.ready'); await pg.evaluate(f'LEGS={json.dumps(LEGS)}')
    await pg.wait_for_timeout(400); return b,pg
async def stills(ts):
    async with async_playwright() as pw:
        b,pg=await pagina(pw)
        json.dump(await pg.evaluate('info()'),open('info.json','w'))
        for t in ts:
            await pg.evaluate(f'render({float(t)})'); await pg.screenshot(path=f'st_{t}.png',omit_background=True)
        await b.close()
async def faixa(k,f0,f1):
    async with async_playwright() as pw:
        b,pg=await pagina(pw)
        ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','image2pipe','-framerate',str(FPS),'-c:v','png','-i','-','-c:v','png','-pix_fmt','rgba',f'ov_{k}.mov'],stdin=subprocess.PIPE)
        for f in range(f0,f1):
            await pg.evaluate(f'render({f/FPS})'); ff.stdin.write(await pg.screenshot(omit_background=True))
        ff.stdin.close(); ff.wait(); await b.close()
if sys.argv[1]=='stills': asyncio.run(stills(sys.argv[2:]))
else: k,f0,f1=map(int,sys.argv[2:5]); asyncio.run(faixa(k,f0,f1))
