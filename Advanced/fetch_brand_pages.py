import json
from pathlib import Path
from urllib.parse import urlparse

import requests


BRANDS = [
    {"brand": "google", "home": "https://www.google.com"},
    {"brand": "paypal", "home": "https://www.paypal.com"},
    {"brand": "amazon", "home": "https://www.amazon.com"},
    {"brand": "microsoft", "home": "https://www.microsoft.com"},
    {"brand": "apple", "home": "https://www.apple.com"},
    {"brand": "facebook", "home": "https://www.facebook.com"},
    {"brand": "instagram", "home": "https://www.instagram.com"},
    {"brand": "linkedin", "home": "https://www.linkedin.com"},
    {"brand": "netflix", "home": "https://www.netflix.com"},
    {"brand": "gamma", "home": "https://gamma.app"},
    {"brand": "myntra", "home": "https://www.myntra.com"},
    {"brand": "boat", "home": "https://www.boat-lifestyle.com"}
]


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def fetch_front_page(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=12)
    r.raise_for_status()
    return r.text


def main() -> None:
    base = Path(__file__).parent
    out_root = base / 'brand_pages'
    ensure_dir(out_root)
    index = []
    for b in BRANDS:
        brand = b['brand']
        home = b['home']
        try:
            html = fetch_front_page(home)
            dom = urlparse(home).netloc
            folder = out_root / brand
            ensure_dir(folder)
            (folder / 'index.html').write_text(html, encoding='utf-8')
            index.append({"brand": brand, "domain": dom, "url": home, "path": str(folder / 'index.html')})
            print(f"Saved {brand}: {home} -> {folder / 'index.html'}")
        except Exception as e:
            print(f"WARN: Failed {brand} {home}: {e}")
    (out_root / 'index.json').write_text(json.dumps(index, indent=2), encoding='utf-8')
    print('Done. Saved HTML front pages. Optional: render to screenshots with your browser for richer pHash sets.')


if __name__ == '__main__':
    main()


