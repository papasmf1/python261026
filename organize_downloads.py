import shutil
from pathlib import Path

DOWNLOADS = Path(r"C:\Users\student\Downloads")

RULES = {
    "images": {".jpg", ".jpeg"},
    "data": {".csv", ".xlsx"},
    "docs": {".txt", ".doc", ".pdf"},
    "archive": {".zip", ".exe"},
}


def unique_path(dest: Path) -> Path:
    if not dest.exists():
        return dest
    n = 1
    while True:
        candidate = dest.with_name(f"{dest.stem}({n}){dest.suffix}")
        if not candidate.exists():
            return candidate
        n += 1


def main() -> None:
    ext_to_folder = {ext: folder for folder, exts in RULES.items() for ext in exts}

    for folder in RULES:
        (DOWNLOADS / folder).mkdir(exist_ok=True)

    for item in DOWNLOADS.iterdir():
        if not item.is_file():
            continue
        folder = ext_to_folder.get(item.suffix.lower())
        if folder is None:
            continue
        target = unique_path(DOWNLOADS / folder / item.name)
        shutil.move(str(item), str(target))
        print(f"{item.name} -> {target}")


if __name__ == "__main__":
    main()
