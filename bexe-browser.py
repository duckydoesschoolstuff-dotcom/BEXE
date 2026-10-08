#!/usr/bin/env python3
import http.server, json, os, shutil, subprocess, tempfile, threading, urllib.parse
from pathlib import Path
from bexe import read
ROOT=Path(__file__).resolve().parent; PORT=8765; TMP=ROOT/'workspace'; TMP.mkdir(exist_ok=True)
HTML='''<!doctype html><meta charset=utf-8><title>BEXE Browser</title><style>body{font:16px system-ui;background:#111;color:#eee;max-width:900px;margin:40px auto}#drop{border:2px dashed #777;padding:70px;text-align:center;border-radius:20px}.on{border-color:#6cf;background:#18222d}button{padding:12px 18px;margin:8px;border-radius:10px;border:0;cursor:pointer}pre{background:#181818;padding:15px;white-space:pre-wrap}small{color:#aaa}</style><h1>BEXE Browser</h1><p>Open a <b>.bexe</b> package containing the original Windows executable.</p><div id=drop>Drop .bexe here<br><button onclick=file.click()>Choose BEXE</button><input id=file type=file accept=.bexe hidden></div><div id=info></div><button id=run disabled>▶ Run</button><pre id=log></pre><script>
let b=null; const drop=document.querySelector('#drop'), file=document.querySelector('#file'), info=document.querySelector('#info'), run=document.querySelector('#run'), log=document.querySelector('#log');
function load(f){b=f; info.textContent=f.name+' — '+(f.size/1048576).toFixed(2)+' MB'; run.disabled=false; log.textContent='BEXE loaded. Click Run.'}
file.onchange=e=>load(e.target.files[0]); ['dragenter','dragover'].forEach(x=>drop.addEventListener(x,e=>{e.preventDefault();drop.classList.add('on')})); ['dragleave','drop'].forEach(x=>drop.addEventListener(x,e=>{e.preventDefault();drop.classList.remove('on')})); drop.addEventListener('drop',e=>load(e.dataTransfer.files[0]));
run.onclick=async()=>{run.disabled=true; log.textContent='Starting compatibility runtime…'; const fd=new FormData(); fd.append('file',b); const r=await fetch('/run',{method:'POST',body:fd}); log.textContent=await r.text(); run.disabled=false};
</script>'''
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path=='/': self.send_response(200); self.send_header('Content-Type','text/html'); self.end_headers(); self.wfile.write(HTML.encode()); return
        self.send_error(404)
    def do_POST(self):
        if self.path!='/run': self.send_error(404); return
        n=int(self.headers.get('Content-Length','0')); body=self.rfile.read(n)
        # Minimal multipart parser sufficient for one file field.
        ctype=self.headers.get('Content-Type',''); boundary=ctype.split('boundary=',1)[-1].encode(); parts=body.split(b'--'+boundary)
        payload=None; name='game.exe'
        for part in parts:
            if b'filename=' in part:
                head,dat=part.split(b'\r\n\r\n',1); dat=dat.rsplit(b'\r\n',1)[0]
                payload=dat; import re; mm=re.search(br'filename="([^"]+)"',head); name=mm.group(1).decode(errors='ignore') if mm else name; break
        if not payload: self.send_error(400,'No file'); return
        src=TMP/'input.bexe'; src.write_bytes(payload)
        try: m,exe=read(src)
        except Exception as e: self.send_error(400,str(e)); return
        out=TMP/(Path(m.get('filename',name)).name); out.write_bytes(exe)
        wine=shutil.which('wine')
        if not wine:
            msg='BEXE loaded successfully, but Wine is not installed.\n\nRun install-linux-runtime.sh, then press Run again.'
        else:
            display=':99'; subprocess.Popen(['Xvfb',display,'-screen','0','1280x720x24'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); import time; time.sleep(.7)
            env=os.environ.copy(); env['DISPLAY']=display; subprocess.Popen([wine,str(out)],env=env,cwd=str(out.parent)); msg='Started '+str(out)+' with Wine on display '+display+'.'
        self.send_response(200); self.send_header('Content-Type','text/plain'); self.end_headers(); self.wfile.write(msg.encode())
if __name__=='__main__': http.server.ThreadingHTTPServer(('127.0.0.1',PORT),H).serve_forever()
