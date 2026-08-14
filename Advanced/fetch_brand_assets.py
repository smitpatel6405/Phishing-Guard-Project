import re
import json
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests


BRANDS = [
    {"brand": "google", "home": "https://www.google.com"},
    {"brand": "paypal", "home": "https://www.paypal.com"},
    {"brand": "amazon", "home": "https://www.amazon.com"},
    {"brand": "myntra", "home": "https://www.myntra.com"},
    {"brand": "boat", "home": "https://www.boat-lifestyle.com"}
]


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def normalize_url(base: str, href: str) -> str:
    try:
        if not href:
            return ''
        if href.startswith('data:'):
            return ''
        if href.startswith('//'):
            parsed = urlparse(base)
            return f"{parsed.scheme}:{href}"
        if href.startswith('http://') or href.startswith('https://'):
            return href
        return urljoin(base if base.endswith('/') else base + '/', href)
    except Exception:
        return ''


def try_download(url: str, dest: Path) -> bool:
    try:
        r = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200 and r.content:
            dest.write_bytes(r.content)
            return True
    except Exception:
        pass
    return False


def fetch_for_brand(brand: str, home: str, out_dir: Path) -> None:
    ensure_dir(out_dir)
    # Try common logo paths
    candidates = [
        '/favicon.ico', '/favicon.png', '/favicon-32x32.png', '/apple-touch-icon.png',
        '/static/logo.png', '/logo.png', '/images/logo.png', '/assets/logo.png'
    ]
    for rel in candidates:
        url = normalize_url(home, rel)
        name = rel.strip('/').replace('/', '_') or 'favicon.ico'
        dest = out_dir / name
        if try_download(url, dest):
            print(f"Saved {brand}: {url} -> {dest}")
    # Try a few likely CDN paths
    cdn_candidates = [
        'https://logo.clearbit.com/' + urlparse(home).netloc,
    ]
    for url in cdn_candidates:
        dest = out_dir / 'clearbit.png'
        if try_download(url, dest):
            print(f"Saved {brand}: {url} -> {dest}")


def main() -> None:
    base = Path(__file__).parent
    assets_root = base / 'brand_assets'
    ensure_dir(assets_root)
    for b in BRANDS:
        out = assets_root / b['brand']
        fetch_for_brand(b['brand'], b['home'], out)
    print('Done fetching assets. Now run: py -3.8 Advanced/create_logo_hashes.py')


if __name__ == '__main__':
    main()


