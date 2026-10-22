import sys, http.server, threading, socketserver, os
from playwright.sync_api import sync_playwright
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(root)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(('127.0.0.1',8771),Q); threading.Thread(target=srv.serve_forever,daemon=True).start()
W=int(sys.argv[1]); H=int(sys.argv[2]); Ps=[float(x) for x in sys.argv[3:]]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
    pg=b.new_page(viewport={'width':W,'height':H})
    errs=[]; pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None); pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:8771/index.html'); pg.wait_for_timeout(1500)
    for P in Ps:
        pg.evaluate(f'__draw({P})'); pg.wait_for_timeout(150)
        pg.screenshot(path=f'/tmp/claude-0/new_{P}.png')
    print(errs); b.close()
