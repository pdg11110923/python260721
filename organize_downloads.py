from pathlib import Path
import shutil
import sys

DOWNLOAD_DIR = Path(r"C:\Users\student\Downloads")
TARGET_FOLDERS = {
    "images": {".jpg", ".jpeg", ".png"},
    "data": {".csv", ".xlsx"},
    "docs": {".txt", ".doc", ".pdf"},
    "archive": {".zip", ".exe"},
}


def ensure_target_folders(base_dir: Path) -> None:
    for folder_name in TARGET_FOLDERS:
        (base_dir / folder_name).mkdir(parents=True, exist_ok=True)


def get_target_folder(file_name: str) -> str | None:
    extension = Path(file_name).suffix.lower()
    for folder_name, extensions in TARGET_FOLDERS.items():
        if extension in extensions:
            return folder_name
    return None


def create_unique_destination(target_dir: Path, source_file: Path) -> Path:
    destination = target_dir / source_file.name
    counter = 1

    while destination.exists():
        stem = source_file.stem
        suffix = source_file.suffix
        destination = target_dir / f"{stem}_{counter}{suffix}"
        counter += 1

    return destination


def organize_downloads(source_dir: Path) -> tuple[list[tuple[str, str]], list[str]]:
    source_dir = source_dir.expanduser().resolve()
    ensure_target_folders(source_dir)

    moved_files: list[tuple[str, str]] = []
    skipped_files: list[str] = []

    for item in source_dir.iterdir():
        if not item.is_file():
            continue

        target_folder = get_target_folder(item.name)
        if target_folder is None:
            skipped_files.append(item.name)
            continue

        target_dir = source_dir / target_folder
        destination = create_unique_destination(target_dir, item)
        shutil.move(str(item), str(destination))
        moved_files.append((item.name, destination.relative_to(source_dir).as_posix()))

    return moved_files, skipped_files


if __name__ == "__main__":
    source_dir = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else DOWNLOAD_DIR
    moved_files, skipped_files = organize_downloads(source_dir)

    print(f"대상 폴더: {source_dir}")
    print(f"이동 완료: {len(moved_files)}개")
    for old_name, new_path in moved_files:
        print(f"- {old_name} -> {new_path}")

    if skipped_files:
        print(f"건너뛴 파일: {len(skipped_files)}개")
        for name in skipped_files:
            print(f"- {name}")
