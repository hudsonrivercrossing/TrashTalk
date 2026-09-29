#!/usr/bin/env python3
"""Transcribe a prerecorded Mandarin-English conversation with AssemblyAI."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from transcription_common import (
    ensure_outputs_available,
    format_duration,
    get_duration_seconds,
    write_outputs,
)


API_BASE = "https://api.assemblyai.com/v2"
POLL_SECONDS = 3
PROMPT = (
    "A two-person conversation spoken primarily in Mandarin Chinese with frequent English code-switching."
)
CJK = r"\u3400-\u9fff"


def request_json(url: str, api_key: str, *, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Authorization": api_key}
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        # API error bodies contain useful diagnostics; never print request headers or credentials.
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"AssemblyAI returned HTTP {error.code}: {detail}") from None
    except urllib.error.URLError as error:
        raise RuntimeError(f"Could not reach AssemblyAI: {error.reason}") from None


def upload_audio(audio: Path, api_key: str) -> str:
    request = urllib.request.Request(
        f"{API_BASE}/upload",
        data=audio.read_bytes(),
        headers={
            "Authorization": api_key,
            "Content-Type": "application/octet-stream",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            upload_url = json.loads(response.read().decode("utf-8")).get("upload_url")
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"AssemblyAI upload returned HTTP {error.code}: {detail}") from None
    except urllib.error.URLError as error:
        raise RuntimeError(f"Could not upload audio to AssemblyAI: {error.reason}") from None
    if not upload_url:
        raise RuntimeError("AssemblyAI upload response did not include an upload URL.")
    return upload_url


def transcribe(audio: Path, api_key: str) -> dict[str, Any]:
    upload_url = upload_audio(audio, api_key)
    submitted = request_json(
        f"{API_BASE}/transcript",
        api_key,
        payload={
            "audio_url": upload_url,
            "speech_models": ["universal-3-5-pro"],
            "prompt": PROMPT,
            "speaker_labels": True,
            "speakers_expected": 2,
        },
    )
    transcript_id = submitted.get("id")
    if not transcript_id:
        raise RuntimeError(f"AssemblyAI did not return a transcript ID: {submitted}")

    while True:
        result = request_json(f"{API_BASE}/transcript/{transcript_id}", api_key)
        status = result.get("status")
        if status == "completed":
            return result
        if status == "error":
            raise RuntimeError(f"AssemblyAI transcription failed: {result.get('error', 'unknown error')}")
        print(f"Transcription status: {status or 'processing'}…", flush=True)
        time.sleep(POLL_SECONDS)


def retrieve_transcript(transcript_id: str, api_key: str) -> dict[str, Any]:
    while True:
        result = request_json(f"{API_BASE}/transcript/{transcript_id}", api_key)
        status = result.get("status")
        if status == "completed":
            return result
        if status == "error":
            raise RuntimeError(f"AssemblyAI transcription failed: {result.get('error', 'unknown error')}")
        print(f"Transcription status: {status or 'processing'}…", flush=True)
        time.sleep(POLL_SECONDS)


def timestamp(milliseconds: int | float) -> str:
    total_seconds = max(0, round(float(milliseconds) / 1000))
    return f"{total_seconds // 60:02d}:{total_seconds % 60:02d}"


def normalize_mixed_text(text: str) -> str:
    """Remove tokenization spaces inside Chinese while preserving English word spacing."""
    text = re.sub(rf"(?<=[{CJK}])\s+(?=[{CJK}])", "", text)
    text = re.sub(r"(?<=[，。！？、；：])\s+", "", text)
    text = re.sub(r"\s+(?=[，。！？、；：])", "", text)
    return text.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audio", type=Path, nargs="+", help="One or more prerecorded audio files")
    parser.add_argument("--transcript-id", help="Save an existing AssemblyAI job instead of submitting audio again")
    parser.add_argument("--check", action="store_true", help="Check local files and configuration without uploading")
    args = parser.parse_args()

    try:
        from dotenv import load_dotenv

        load_dotenv(Path(__file__).with_name(".env.local"), override=True)
    except ImportError:
        print("Error: python-dotenv is missing. Run `python -m pip install -r requirements.txt`.", file=sys.stderr)
        return 2

    api_key = os.environ.get("ASSEMBLYAI_API_KEY")
    if not api_key and not args.check:
        print(
            "Error: ASSEMBLYAI_API_KEY is missing. Add it to .env.local or the environment. No upload was made.",
            file=sys.stderr,
        )
        return 2

    output_dir = Path(__file__).with_name("transcripts") / "assemblyai"
    jobs: list[tuple[Path, float | None, Path, Path]] = []
    try:
        for audio_arg in args.audio:
            audio = audio_arg.expanduser().resolve()
            if not audio.is_file():
                raise ValueError(f"Audio file not found: {audio}")
            if audio.suffix.lower() not in {".m4a", ".mp3", ".wav", ".mp4", ".flac", ".ogg", ".webm"}:
                raise ValueError(f"Unsupported audio file type: {audio.suffix}")
            duration = get_duration_seconds(audio)
            audio_output_dir = output_dir / audio.stem
            json_path = audio_output_dir / f"{audio.stem}.assemblyai.diarized.json"
            text_path = audio_output_dir / f"{audio.stem}.assemblyai.diarized.txt"
            ensure_outputs_available(json_path, text_path)
            jobs.append((audio, duration, json_path, text_path))
    except (ValueError, FileExistsError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    for audio, duration, _, _ in jobs:
        duration_note = f", {format_duration(duration)}" if duration is not None else ""
        print(f"File: {audio} ({audio.stat().st_size / (1024 * 1024):.1f} MiB{duration_note})")
    if args.check:
        key_note = "AssemblyAI key is configured." if api_key else "AssemblyAI key is not configured yet."
        print(f"Local preflight passed. {key_note} No upload was made.")
        return 0

    try:
        for index, (audio, duration, json_path, text_path) in enumerate(jobs, start=1):
            json_path.parent.mkdir(parents=True, exist_ok=True)
            if args.transcript_id:
                print(f"Retrieving existing transcript {args.transcript_id}…", flush=True)
                result = retrieve_transcript(args.transcript_id, api_key)
            else:
                print(f"Uploading and transcribing {index}/{len(jobs)}…", flush=True)
                result = transcribe(audio, api_key)
            utterances = result.get("utterances") or []
            readable_utterances = [
                {**item, "text": normalize_mixed_text(item.get("text", ""))}
                for item in utterances
            ]
            if utterances:
                lines = [
                    f"[{timestamp(item['start'])}-{timestamp(item['end'])}] "
                    f"Speaker {item.get('speaker') or '?'}: {item.get('text', '')}"
                    for item in readable_utterances
                ]
            else:
                lines = [normalize_mixed_text(result.get("text", ""))]
            if not any(lines):
                raise RuntimeError("AssemblyAI returned no transcript text.")

            write_outputs(
                json_path,
                text_path,
                {
                    "provider": "assemblyai",
                    "model": result.get("speech_model_used", "universal-3-5-pro"),
                    "transcript_id": result.get("id"),
                    "source": str(audio),
                    "duration_seconds": duration,
                    "prompt": PROMPT,
                    "speakers_expected": 2,
                    "text": normalize_mixed_text(result.get("text", "")),
                    "raw_text": result.get("text", ""),
                    "utterances": readable_utterances,
                    "raw_utterances": utterances,
                },
                "\n".join(lines),
            )
            print(f"Transcript: {text_path}\nStructured data: {json_path}")
    except Exception as error:
        print(f"Transcription failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
