from __future__ import annotations

import argparse
import hashlib
import subprocess
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

EXCLUDED_PATHS = {
    "logs/agent_system.log",
}

EXCLUDED_PREFIXES = (
    ".github/",
    ".vscode/",
    "app/tests/",
    "docs/v7",
    "docs/v8",
    "docs/v9",
    "docs/v10",
    "docs/v11",
    "transition/",
)


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def should_include(relative_path: str) -> bool:
    normalized = relative_path.replace("\\", "/")

    if normalized in EXCLUDED_PATHS:
        return False

    if normalized.startswith(EXCLUDED_PREFIXES):
        return False

    return True


def calculate_sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def build(version: str, output_directory: Path) -> tuple[Path, Path]:
    output_directory.mkdir(parents=True, exist_ok=True)

    artifact_name = f"ai-summarizer-v{version}.zip"
    artifact_path = output_directory / artifact_name

    files = [
        relative_path
        for relative_path in tracked_files()
        if should_include(relative_path)
    ]

    with zipfile.ZipFile(
        artifact_path,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
    ) as archive:
        for relative_path in sorted(files):
            source = PROJECT_ROOT / relative_path

            if not source.is_file():
                continue

            archive.write(
                source,
                arcname=f"ai-summarizer-v{version}/{relative_path}",
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
        description="Build the certified AI Summarizer source release artifact."
    )

    parser.add_argument(
        "--version",
        required=True,
        help="Release version, for example 12.0.0-m4",
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
