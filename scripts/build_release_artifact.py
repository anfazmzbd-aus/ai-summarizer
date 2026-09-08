from __future__ import annotations

import argparse
import hashlib
import subprocess
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

ROOT_FILES = {
    ".env.example",
    "CHANGELOG.md",
    "README.md",
    "requirements.txt",
}

ALLOWED_PREFIXES = (
    "app/",
    "docs/v12/",
    "static/",
)

ALLOWED_SCRIPT_FILES = {
    "scripts/build_release_artifact.py",
    "scripts/validate_runtime.py",
}

EXCLUDED_APP_PREFIXES = (
    "app/tests/",
    "app/legacy/",
)

EXCLUDED_FILE_SUFFIXES = (
    ".pyc",
    ".pyo",
)

# ZIP timestamps cannot represent dates before 1980.
# A fixed timestamp makes release construction independent of
# source-file mtimes.
DETERMINISTIC_TIMESTAMP = (1980, 1, 1, 0, 0, 0)

# Regular file permissions: rw-r--r--
DETERMINISTIC_EXTERNAL_ATTR = 0o100644 << 16


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    return [
        line.strip().replace("\\", "/")
        for line in result.stdout.splitlines()
        if line.strip()
    ]


def should_include(relative_path: str) -> bool:
    normalized = relative_path.replace("\\", "/")

    if normalized in ROOT_FILES:
        return True

    if normalized in ALLOWED_SCRIPT_FILES:
        return True

    if normalized.startswith(EXCLUDED_APP_PREFIXES):
        return False

    if normalized.endswith(EXCLUDED_FILE_SUFFIXES):
        return False

    if normalized.startswith(ALLOWED_PREFIXES):
        return True

    return False


def calculate_sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def _write_deterministic_file(
    archive: zipfile.ZipFile,
    source: Path,
    archive_name: str,
) -> None:
    info = zipfile.ZipInfo(
        filename=archive_name,
        date_time=DETERMINISTIC_TIMESTAMP,
    )
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = DETERMINISTIC_EXTERNAL_ATTR
    info.create_system = 3

    archive.writestr(
        info,
        source.read_bytes(),
    )


def build(version: str, output_directory: Path) -> tuple[Path, Path]:
    output_directory.mkdir(parents=True, exist_ok=True)

    artifact_name = f"ai-summarizer-v{version}.zip"
    artifact_path = output_directory / artifact_name

    files = sorted(
        relative_path
        for relative_path in tracked_files()
        if should_include(relative_path)
    )

    with zipfile.ZipFile(
        artifact_path,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
    ) as archive:
        for relative_path in files:
            source = PROJECT_ROOT / relative_path

            if not source.is_file():
                continue

            _write_deterministic_file(
                archive=archive,
                source=source,
                archive_name=(f"ai-summarizer-v{version}/{relative_path}"),
            )

    checksum = calculate_sha256(artifact_path)

    checksum_path = output_directory / f"{artifact_name}.sha256"
    checksum_path.write_text(
        f"{checksum}  {artifact_name}\n",
        encoding="utf-8",
    )

    return artifact_path, checksum_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description=("Build the certified AI Summarizer source release artifact.")
    )

    parser.add_argument(
        "--version",
        required=True,
        help="Release version, for example 12.0.0-m5",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "dist",
        help="Artifact output directory.",
    )

    args = parser.parse_args()

    artifact_path, checksum_path = build(
        version=args.version,
        output_directory=args.output,
    )

    print(f"Artifact: {artifact_path}")
    print(f"Checksum: {checksum_path}")


if __name__ == "__main__":
    main()
