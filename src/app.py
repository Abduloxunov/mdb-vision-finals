"""Loopback CarDoctor server. Public hosting needs a production gateway."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
import argparse,atexit,json,mimetypes,secrets,threading,traceback
from pipeline import Pipeline,report,ROOT
from assess import Assessor
TOKEN=secrets.token_urlsafe(32)
PIPELINE=None
ASSESSOR=None
WARM={'state':'loading'}
def warmup():
    """Load the damage model and text index at startup so the first check is fast (no downloads; local files only)."""
    try:
        with PIPELINE.lock:
            from PIL import Image
            try:PIPELINE.model().predict(Image.new('RGB',(384,384),'gray'),threshold=0.5)
            except ValueError as exc:
                print('Damage model not loaded:',exc,flush=True);WARM['state']='no_checkpoint'
            try:
                if PIPELINE.retriever is None:
                    from vector_store import VectorKB
                    PIPELINE.retriever=VectorKB()
                PIPELINE.retriever.query('warm up',part='body')
            except Exception as exc:print('Vector index not loaded (keyword search still works):',type(exc).__name__,flush=True)
        if WARM['state']=='loading':WARM['state']='ready'
        print('CarDoctor warm-up finished:',WARM['state'],flush=True)
    except Exception:
        WARM['state']='failed';traceback.print_exc()
PORT=8766
class Handler(BaseHTTPRequestHandler):
    def send(self,body,status=200,kind='application/json; charset=utf-8'):
        if not isinstance(body,bytes):body=json.dumps(body,ensure_ascii=False,allow_nan=False).encode()
        self.send_response(status)
        for key,value in {'Content-Type':kind,'Content-Length':str(len(body)),'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','Content-Security-Policy':"default-src 'self'; img-src 'self' data: blob:; style-src 'self'; script-src 'self'; connect-src 'self'; frame-ancestors 'none'"}.items():self.send_header(key,value)
        self.end_headers();self.wfile.write(body)
    def valid_host(self):return self.headers.get('Host') in {f'127.0.0.1:{PORT}',f'localhost:{PORT}'}
    def do_GET(self):
        if not self.valid_host():return self.send({'error':'Invalid host.'},400)
        path=urlsplit(self.path).path
        if path=='/api/health':return self.send({'token':TOKEN,'checkpoint_available':PIPELINE.checkpoint.is_file() and PIPELINE.checkpoint.stat().st_size>1000000,'model':'RF-DETR Nano','private_local_demo':True,'warm':WARM['state']})
        static={'/':'index.html','/app.js':'app.js','/style.css':'style.css','/favicon.svg':'favicon.svg'}
        if path in static:
            file=ROOT/'web'/static[path]
            return self.send(file.read_bytes(),kind=mimetypes.guess_type(str(file))[0] or 'text/plain')
        return self.send({'error':'Not found.'},404)
    def do_POST(self):
        if not self.valid_host():return self.send({'error':'Invalid host.'},400)
        if self.headers.get('X-CarDoctor-Token')!=TOKEN:return self.send({'error':'Reload the app before submitting.'},403)
        if self.headers.get('Content-Type','').split(';')[0]!='application/json':return self.send({'error':'Send JSON.'},415)
        path=urlsplit(self.path).path
        if path not in {'/api/analyze','/api/assess'}:return self.send({'error':'Not found.'},404)
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=(12 if path=='/api/analyze' else 40)*1024*1024:return self.send({'error':'Photos are too large. Use fewer or smaller photos.'},413)
            data=json.loads(self.rfile.read(size))
            if path=='/api/assess':
                # Whole-car check: several photos, combined report. Validation messages are safe to show.
                try:return self.send(ASSESSOR.assess(data))
                except ValueError as exc:return self.send({'error':str(exc)},400)
            result=PIPELINE.analyze(data)
            result['report']=report(result)
            return self.send(result)
        except BlockingIOError as exc:return self.send({'error':str(exc)},429)
        except (ValueError,TypeError,KeyError,UnicodeDecodeError):return self.send({'error':'Invalid image or context. Add a symptom description or JPEG/PNG/WebP photo under 8 MB and confirm the selected fields.'},400)
        except Exception as exc:
            print('Analysis failed:',type(exc).__name__,flush=True)
            traceback.print_exc()
            return self.send({'error':'Analysis could not complete. Check the server setup and checkpoint.'},500)
    def log_message(self,*args):pass
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=8766)
    parser.add_argument('--checkpoint',type=Path)
    args=parser.parse_args();PORT=args.port;PIPELINE=Pipeline(args.checkpoint);ASSESSOR=Assessor(PIPELINE)
    atexit.register(PIPELINE.close)
    threading.Thread(target=warmup,daemon=True).start()
    print(f'CarDoctor: http://127.0.0.1:{PORT}',flush=True)
    ThreadingHTTPServer(('127.0.0.1',PORT),Handler).serve_forever()
