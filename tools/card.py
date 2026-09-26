#!/usr/bin/env python3
"""Share card: draw a 1200x630 page and photograph it with headless Chrome -> docs/card.png

    python3 tools/card.py
"""
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "card.png"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

PAGE = """<!doctype html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box;margin:0}
body{width:1200px;height:630px;overflow:hidden;background:#f4ead5;color:#1d1611;
  font-family:Rockwell,"Rockwell Nova","Roboto Slab",Georgia,serif;position:relative}
.fascia{position:absolute;left:0;right:0;height:18px;
  background:linear-gradient(#f47b20 0 33.4%,#e4252c 33.4% 66.7%,#00815d 66.7%)}
.fascia.top{top:0}.fascia.bottom{bottom:0}
.stripes{position:absolute;left:0;right:0;height:46px;
  background:repeating-linear-gradient(90deg,#b3261e 0 46px,#f4ead5 46px 92px)}
.stripes.top{top:18px}.stripes.bottom{bottom:18px}
.scallop{position:absolute;top:64px;left:0;right:0;height:40px;
  background:repeating-linear-gradient(90deg,#b3261e 0 46px,#f4ead5 46px 92px);
  -webkit-mask:radial-gradient(24px 22px at 23px 0,#000 98%,transparent) 0 0/46px 40px repeat-x}
.main{position:absolute;top:128px;left:0;right:0;text-align:center}
.bill{display:inline-flex;align-items:center;gap:12px;border:4px solid #1d1611;padding:8px 22px;font-weight:700;font-size:20px;
  letter-spacing:.32em;text-transform:uppercase;background:#fffaf0}
.bill svg{width:22px;height:22px}
.bill .th{letter-spacing:0;font:600 20px/1 Thonburi,"Noto Sans Thai",Tahoma,sans-serif;text-transform:none}
.side{position:absolute;top:210px}
.side.l{left:92px;transform:rotate(-10deg)}.side.r{right:96px;transform:rotate(8deg)}
h1{font-weight:900;font-size:118px;line-height:.9;text-transform:uppercase;margin-top:22px;letter-spacing:-.01em}
h1 .one{display:block;font-size:44px;letter-spacing:.4em;color:#b3261e;margin-bottom:6px}
h1 .show{color:#b3261e}
p{font-family:Georgia,serif;font-style:italic;font-size:30px;color:#5e5246;margin-top:24px}
.stars{color:#c8922a;font-size:22px;letter-spacing:.6em;margin-top:14px}
</style></head><body>
<div class="fascia top"></div><div class="stripes top"></div><div class="scallop"></div>
<div class="main">
  <span class="bill"><svg viewBox="0 0 24 24"><path d="M12 2.5a6.2 6.2 0 0 0-6.2 6.2v4.1L3.6 16h16.8l-2.2-3.2V8.7A6.2 6.2 0 0 0 12 2.5z" fill="#1d1611"/><circle cx="12" cy="19.4" r="2.3" fill="#1d1611"/></svg>Hello, welcome <span class="th">สวัสดีค่ะ</span></span>
  <h1><span class="one">The</span>One Man <span class="show">Sideshow</span></h1>
  <p>A sourced city directory in thirty-five hours.</p>
  <div class="stars">&#9733; &#9733; &#9733;</div>
</div>
<svg class="side l" width="84" height="232" viewBox="0 0 40 112"><rect x="16" y="64" width="8" height="46" rx="4" fill="#d6a36a"/><path d="M4 20a16 16 0 0 1 32 0v46a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4z" fill="#ff5f8f"/><path d="M10 17v44" stroke="#fff" stroke-opacity=".45" stroke-width="3.5" stroke-linecap="round"/></svg>
<svg class="side r" width="72" height="221" viewBox="0 0 30 92"><path d="M11 3h8v15c0 5 7 9 7 18v51c0 2.5-2 4-4 4H8c-2 0-4-1.5-4-4V36c0-9 7-13 7-18z" fill="#6e3710"/><rect x="10" y="0" width="10" height="6" rx="1.5" fill="#d9b44a"/><rect x="4" y="47" width="22" height="22" rx="2" fill="#f1dfae"/><rect x="4" y="52" width="22" height="5" fill="#e4252c"/><path d="M8.5 40v42" stroke="#fff" stroke-opacity=".35" stroke-width="2.5" stroke-linecap="round"/></svg>
<div class="stripes bottom"></div><div class="fascia bottom"></div>
</body></html>"""


def main():
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "card.html"
        page.write_text(PAGE, encoding="utf-8")
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=1", "--window-size=1200,630",
                        f"--screenshot={OUT}", page.as_uri()],
                       check=True, capture_output=True, timeout=60)
    print(OUT)


if __name__ == "__main__":
    main()
