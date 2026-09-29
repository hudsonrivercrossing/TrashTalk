"""Shared local checks and output helpers for transcription scripts."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


def get_duration_seconds(path: Path) -> float | None:
    afinfo = shutil.which("afinfo")
    if afinfo:
        result = subprocess.run(
            [afinfo, str(path)], capture_output=True, text=True, check=False
        )
        for line in result.stdout.splitlines():
            if "estimated duration" in line.lower():
                try:
                    return float(line.split(":", 1)[1].strip().split()[0])
                except (IndexError, ValueError):
                    break

    ffprobe = shutil.which("ffprobe")
    if ffprobe:
        result = subprocess.run(
            [
                ffprobe,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            try:
                return float(result.stdout.strip())
            except ValueError:
                pass
    return None


def format_duration(seconds: float) -> str:
    total = round(seconds)
    return f"{total // 60}:{total % 60:02d}"


def ensure_outputs_available(*paths: Path) -> None:
    existing = [str(path) for path in paths if path.exists()]
    if existing:
        raise FileExistsError(
            "Refusing to overwrite existing output(s): " + ", ".join(existing)
        )


def write_outputs(json_path: Path, text_path: Path, data: dict[str, Any], text: str) -> None:
    ensure_outputs_available(json_path, text_path)
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    text_path.write_text(text.rstrip() + "\n", encoding="utf-8")
