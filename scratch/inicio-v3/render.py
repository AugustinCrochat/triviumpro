"""Captura páginas con Chrome sin cabeza (DevTools), esperando la tipografía. Si Archivo no carga, corta:
con captura directa algunas portadas salían en silencio con la fuente de reemplazo."""
import base64, json, os, socket, struct, subprocess, tempfile, time, urllib.request

PUERTO = 9347


class Chrome:
    def __enter__(self):
        self.p = subprocess.Popen(['google-chrome', '--headless=new', '--disable-gpu', '--hide-scrollbars', '--allow-file-access-from-files',
                                   f'--remote-debugging-port={PUERTO}', f'--user-data-dir={tempfile.mkdtemp()}', 'about:blank'],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(100):
            try:
                tabs = json.load(urllib.request.urlopen(f'http://127.0.0.1:{PUERTO}/json'))
                url = next(t for t in tabs if t['type'] == 'page')['webSocketDebuggerUrl']
                break
            except Exception:
                time.sleep(.2)
        self.s = socket.create_connection(('127.0.0.1', PUERTO), timeout=60)
        clave = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall(f'GET {url.split(str(PUERTO), 1)[1]} HTTP/1.1\r\nHost: 127.0.0.1:{PUERTO}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {clave}\r\nSec-WebSocket-Version: 13\r\n\r\n'.encode())
        self.f = self.s.makefile('rb')
        while self.f.readline() != b'\r\n':
            pass
        self.n = 0
        return self

    def __exit__(self, *a):
        self.p.terminate()

    def llamar(self, metodo, **params):
        self.n += 1
        d = json.dumps({'id': self.n, 'method': metodo, 'params': params}).encode()
        m, n = os.urandom(4), len(d)
        cab = b'\x81' + (bytes([128 | n]) if n < 126 else bytes([254]) + struct.pack('>H', n) if n < 65536 else bytes([255]) + struct.pack('>Q', n))
        self.s.sendall(cab + m + bytes(b ^ m[i % 4] for i, b in enumerate(d)))
        while True:
            datos = b''
            while True:
                b0, b1 = self.f.read(2); largo = b1 & 127
                if largo == 126: largo = struct.unpack('>H', self.f.read(2))[0]
                elif largo == 127: largo = struct.unpack('>Q', self.f.read(8))[0]
                datos += self.f.read(largo)
                if b0 & 128: break
            r = json.loads(datos)
            if r.get('id') == self.n:
                return r.get('result', r)

    def capturar(self, url, png, ancho=1100, alto=600):
        self.llamar('Emulation.setDeviceMetricsOverride', width=ancho, height=alto, deviceScaleFactor=1, mobile=False)
        expr = """(async()=>{while(document.readyState!=='complete')await new Promise(r=>setTimeout(r,100));
          const f=await document.fonts.load('800 50px Archivo','Aá');await document.fonts.ready;
          await Promise.all([...document.images].map(i=>i.decode()));return f.length>0})()"""
        for intento in range(3):
            self.llamar('Page.navigate', url=url)
            time.sleep(.5 + intento * 2)
            r = self.llamar('Runtime.evaluate', expression=expr, awaitPromise=True, returnByValue=True)
            if r.get('result', {}).get('value') is True:
                break
        else:
            raise SystemExit(f'La tipografía o una imagen no cargó en {url}')
        time.sleep(.3)
        with open(png, 'wb') as fh:
            fh.write(base64.b64decode(self.llamar('Page.captureScreenshot', format='png')['data']))
