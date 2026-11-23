import re
from html import unescape
from urllib.request import Request, urlopen

def extract_link_metadata(url: str, timeout: float = 5.0):
    u = (url or "").strip()
    if not u.startswith(("http://", "https://")):
        raise ValueError("Invalid URL scheme")
    req = Request(u, headers={"User-Agent": "RecallBot/1.0"})
    with urlopen(req, timeout=timeout) as resp:
        html = resp.read(200000).decode("utf-8", errors="replace")
    tm = re.search("<title[^>]*>(.*?)</title>", html, flags=re.I | re.S)
    title = re.sub(r"\s+", " ", unescape(tm.group(1))).strip()[:250] if tm else None
    return {"title": title or None, "description": None}
