"""Build a deterministic zip archive for an Agent Skill.

The script is dependency-free and intentionally refuses symlinks so a skill
archive cannot accidentally include content outside its directory.
"""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path
from typing import Iterable


SKIP_NAMES = {".DS_Store"}
SKIP_SUFFIXES = {".pyc", ".pyo"}
SKIP_PARTS = {"__pycache__"}
FIXED_ZIP_TIME = (2020, 1, 1, 0, 0, 0)


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def collect_skill_files(skill_dir: Path) -> list[Path]:
    skill_dir = skill_dir.resolve()
    if not skill_dir.is_dir():
        raise ValueError(f"skill directory not found: {skill_dir}")
    if not (skill_dir / "SKILL.md").is_file():
        raise ValueError("skill directory must contain SKILL.md")

    files: list[Path] = []
    for path in sorted(skill_dir.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"symlinks are not allowed in skill archives: {path}")
        if not path.is_file():
            continue
        rel = path.relative_to(skill_dir)
        if any(part in SKIP_PARTS for part in rel.parts):
            continue
        if path.name in SKIP_NAMES or path.suffix in SKIP_SUFFIXES:
            continue
        files.append(path)
    return files


def build_skill_archive(skill_dir: Path, output: Path) -> Path:
    skill_dir = skill_dir.resolve()
    output = output.resolve()

    if _is_relative_to(output, skill_dir):
        raise ValueError("output archive must be outside the skill directory")

    files = collect_skill_files(skill_dir)
    output.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(
        output,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for path in files:
            rel = path.relative_to(skill_dir)
            arcname = (Path(skill_dir.name) / rel).as_posix()
            info = zipfile.ZipInfo(arcname, date_time=FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())

    return output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Package an Agent Skill directory as a deterministic zip."
    )
    parser.add_argument("skill_dir", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        help="Archive path. Defaults to dist/<skill-name>.zip.",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    skill_dir = args.skill_dir
    output = args.output or Path("dist") / f"{skill_dir.name}.zip"
    try:
        built = build_skill_archive(skill_dir, output)
    except ValueError as exc:
        raise SystemExit(f"error: {exc}") from exc
    print(built)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
