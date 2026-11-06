"""Lægger en video i køen som en Reel.

Brug: python3 scripts/enqueue_video.py <video.mp4> <tidspunkt> <slug> <billedtekst-fil> [forside-sekund]
  tidspunkt: "2026-11-09 19:00" (dansk tid) eller "næste" = næste ledige plads efter config.json
  slug: kort navn, fx "big-plans"

Videoen genkodes til Instagrams Reels-format: 1080x1920, H.264, AAC, 30 fps, maks. 90 sek.
"""
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
TZ = ZoneInfo(CONFIG.get("tidszone", "Europe/Copenhagen"))


def taken():
    out = set()
    for f in (ROOT / "queue").glob("*/opslag.json"):
        q = json.loads(f.read_text(encoding="utf-8"))
        if q.get("status") in ("klar", "postet"):
            out.add(datetime.fromisoformat(q["tidspunkt"]).astimezone(TZ).replace(second=0, microsecond=0))
    return out


def next_slot():
    days = CONFIG.get("postdage", [0, 2, 5])  # mandag, onsdag, lørdag
    hh, mm = map(int, CONFIG.get("tid", "19:00").split(":"))
    busy = taken()
    d = datetime.now(TZ).replace(hour=hh, minute=mm, second=0, microsecond=0)
    if d <= datetime.now(TZ) + timedelta(hours=2):
        d += timedelta(days=1)
    while True:
        if d.weekday() in days and d not in busy:
            return d
        d += timedelta(days=1)


def main(video, when, slug, caption_file, cover=None):
    t = next_slot() if when == "næste" else datetime.strptime(when, "%Y-%m-%d %H:%M").replace(tzinfo=TZ)
    name = f"{t:%Y-%m-%d-%H%M}-{slug}"
    dest = ROOT / "queue" / name
    dest.mkdir(parents=True, exist_ok=True)
    out = dest / "video.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video,
                    "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease:flags=lanczos,"
                           "pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=30",
                    "-t", "90", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-profile:v", "high",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-ar", "48000",
                    "-movflags", "+faststart", str(out)], check=True)
    caption = Path(caption_file).read_text(encoding="utf-8").strip()
    opslag = {"tidspunkt": t.isoformat(), "status": "klar", "type": "reel", "titel": slug,
              "video": "video.mp4", "billedtekst": caption, "note": ""}
    if cover is not None:
        opslag["forside_sekund"] = float(cover)
    (dest / "opslag.json").write_text(json.dumps(opslag, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{name}: {t:%a %d.%m kl. %H:%M}, {out.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main(*sys.argv[1:6])
