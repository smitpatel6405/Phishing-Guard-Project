import json
import os
import subprocess
import shutil
from pathlib import Path


POSSIBLE_CHROME = [
    r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    shutil.which("chrome"),
    shutil.which("google-chrome"),
    shutil.which("chromium"),
]


def find_chrome() -> str:
    for p in POSSIBLE_CHROME:
        if p and Path(p).exists():
            return p
    raise FileNotFoundError("Chrome/Chromium not found. Please install Google Chrome.")


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def render(url: str, out_png: Path, chrome_path: str) -> None:
    ensure_dir(out_png.parent)
    args = [
        chrome_path,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--window-size=1366,768",
        f"--screenshot={str(out_png)}",
        url,
    ]
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main() -> None:
    base = Path(__file__).parent
    idx_path = base / 'brand_pages' / 'index.json'
    if not idx_path.exists():
        print("brand_pages/index.json not found. Run fetch_brand_pages.py first.")
        return
    data = json.loads(idx_path.read_text(encoding='utf-8'))
    chrome = find_chrome()
    for entry in data:
        brand = entry.get('brand')
        url = entry.get('url')
        if not brand or not url:
            continue
        out_png = base / 'brand_assets' / brand / 'screenshot.png'
        try:
            render(url, out_png, chrome)
            print(f"Rendered {brand}: {url} -> {out_png}")
        except Exception as e:
            print(f"WARN: Failed render {brand}: {e}")
    print("Done. Now run: py -3.8 Advanced/create_logo_hashes.py")


if __name__ == '__main__':
    main()


