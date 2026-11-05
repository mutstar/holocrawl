from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import argparse,json

parser=argparse.ArgumentParser()
parser.add_argument('--root',required=True)
parser.add_argument('--port',type=int,default=8797)
args=parser.parse_args()
preview_root=Path(args.root).resolve()
class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.split('?',1)[0]=='/__holocrawl_home_health.json':
            data=json.dumps({'app':'HoloCrawl-home-20261104','root':str(preview_root),'port':args.port}).encode()
            self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
        else:super().do_GET()
    def end_headers(self):
        self.send_header('Cache-Control','no-store')
        super().end_headers()
class PreviewServer(ThreadingHTTPServer):
    # A floor preview requests many tile patches concurrently.
    request_queue_size=128
server=PreviewServer(('127.0.0.1',args.port),partial(Handler,directory=str(preview_root)))
print(f'HoloCrawl preview: http://127.0.0.1:{args.port}/city-explore01/',flush=True)
server.serve_forever()
