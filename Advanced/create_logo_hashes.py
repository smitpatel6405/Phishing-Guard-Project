import json
import sys
from pathlib import Path

try:
    from PIL import Image
    import imagehash
except Exception as e:
    print("ERROR: Pillow and ImageHash are required. Install with: py -3.8 -m pip install Pillow ImageHash")
    sys.exit(1)


def compute_phash(image_path: Path) -> str:
    img = Image.open(str(image_path)).convert('RGB')
    # Normalize size for stable hashing
    max_w = 512
    if img.width > max_w:
        img = img.resize((max_w, int(max_w * img.height / max(1, img.width))), Image.BILINEAR)
    return imagehash.phash(img).hash.astype(int).tolist(), imagehash.phash(img).__str__()


def ensure_dirs(base: Path) -> None:
    (base / 'brand_assets').mkdir(exist_ok=True)


def load_logo_db(json_path: Path) -> dict:
    if not json_path.exists():
        return {"phash_bits": 64, "threshold": 12, "logos": []}
    try:
        return json.loads(json_path.read_text(encoding='utf-8'))
    except Exception:
        return {"phash_bits": 64, "threshold": 12, "logos": []}


def save_logo_db(json_path: Path, db: dict) -> None:
    json_path.write_text(json.dumps(db, indent=2, ensure_ascii=False), encoding='utf-8')


def main() -> None:
    base = Path(__file__).parent
    ensure_dirs(base)
    assets = base / 'brand_assets'
    db_path = base / 'logo_hashes.json'
    db = load_logo_db(db_path)

    # Build brand -> entry map
    brand_to_entry = {}
    for entry in db.get('logos', []):
        brand_to_entry[entry.get('brand', '').lower()] = entry

    # Iterate brand directories
    for brand_dir in assets.iterdir():
        if not brand_dir.is_dir():
            continue
        brand = brand_dir.name.lower()
        entry = brand_to_entry.get(brand)
        if not entry:
            entry = {"brand": brand, "hashes": []}
            db.setdefault('logos', []).append(entry)
            brand_to_entry[brand] = entry

        # Compute pHash for each image
        changed = False
        for img_path in brand_dir.glob('*'):
            if img_path.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}:
                continue
            try:
                _, hex_hash = compute_phash(img_path)
                if hex_hash not in entry['hashes']:
                    entry['hashes'].append(hex_hash)
                    changed = True
                    print(f"Added hash for {brand}: {img_path.name} -> {hex_hash}")
            except Exception as e:
                print(f"WARN: Failed to hash {img_path}: {e}")

        if changed:
            # de-duplicate
            entry['hashes'] = sorted(list({h for h in entry['hashes']}))

    save_logo_db(db_path, db)
    print("Done. Updated:", db_path)
    print("Tip: Place logo images under Advanced/brand_assets/<brand>/* and rerun.")


if __name__ == '__main__':
    main()


