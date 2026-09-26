#!/usr/bin/env python3
"""Serve docs/ on localhost for a preview.   python3 tools/serve.py [port]"""
import functools, http.server, os, sys
SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs")
os.chdir(SITE)
port = int(sys.argv[1]) if len(sys.argv) > 1 else 8866
h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=SITE)
http.server.ThreadingHTTPServer(("127.0.0.1", port), h).serve_forever()
