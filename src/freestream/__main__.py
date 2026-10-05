#!/usr/bin/env python3
"""FreeStream â€” Movie, TV, and Anime CLI."""
import os, sys, warnings
os.environ["PYTHONWARNINGS"] = "ignore"
warnings.filterwarnings("ignore"); warnings.simplefilter("ignore")
import subprocess, shutil, time, socket, signal, atexit, tempfile
import threading, platform, re, json, base64, urllib3, webbrowser, random
import concurrent.futures as cf
import contextlib
import queue as _queue
from pathlib import Path
from urllib.parse import urlparse, urlencode, urlunparse, parse_qsl, unquote, quote

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPT_FILE = Path(__file__).resolve()
VENV_DIR = SCRIPT_DIR / ".freestream_venv"
READY_MARKER = VENV_DIR / ".ready"
DOWNLOAD_LOG = SCRIPT_DIR / "download_error.log"

EMBEDDED_OS_API_KEY = "JOUgS9vO6BwbGbKw4lWk6NWXkqD2ajW4"
EMBEDDED_OS_USERNAME = "Freestream"
EMBEDDED_OS_PASSWORD = "Freestream@123@321"

PYTHON_PACKAGES = [
    "rich>=13.0", "InquirerPy>=0.3.4", "requests>=2.31", "urllib3>=2.0",
    "patchright>=1.40",
    "yt-dlp[curl-cffi]>=2024.0", "static-ffmpeg>=2.0",
    "prompt-toolkit>=3.0", "opensubtitlescom>=0.1.5,<0.2",
    "vidsrc-dlp>=0.1.0",
]

_IN_ALT_SCREEN = False
_SPAWNED_PROCS = []
MOVIE_PROBE_CONCURRENCY = 6
ANIME_PROBE_CONCURRENCY = 6
PROBE_CONCURRENCY = MOVIE_PROBE_CONCURRENCY

# â•â• LOGO SIZES â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
LOGO_LARGE = [
    " â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•— â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•— â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•— â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•— â–ˆâ–ˆâ–ˆâ•—   â–ˆâ–ˆâ–ˆâ•—",
    " â–ˆâ–ˆâ•”â•â•â•â•â•â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—â–ˆâ–ˆâ•”â•â•â•â•â•â–ˆâ–ˆâ•”â•â•â•â•â•â–ˆâ–ˆâ•”â•â•â•â•â•â•šâ•â•â–ˆâ–ˆâ•”â•â•â•â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—â–ˆâ–ˆâ•”â•â•â•â•â•â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ•— â–ˆâ–ˆâ–ˆâ–ˆâ•‘",
    " â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•”â•â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—   â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•”â•â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•‘â–ˆâ–ˆâ•”â–ˆâ–ˆâ–ˆâ–ˆâ•”â–ˆâ–ˆâ•‘",
    " â–ˆâ–ˆâ•”â•â•â•  â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—â–ˆâ–ˆâ•”â•â•â•  â–ˆâ–ˆâ•”â•â•â•  â•šâ•â•â•â•â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—â–ˆâ–ˆâ•”â•â•â•  â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘â•šâ–ˆâ–ˆâ•”â•â–ˆâ–ˆâ•‘",
    " â–ˆâ–ˆâ•‘     â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘ â•šâ•â• â–ˆâ–ˆâ•‘",
    " â•šâ•â•     â•šâ•â•  â•šâ•â•â•šâ•â•â•â•â•â•â•â•šâ•â•â•â•â•â•â•â•šâ•â•â•â•â•â•â•   â•šâ•â•   â•šâ•â•  â•šâ•â•â•šâ•â•â•â•â•â•â•â•šâ•â•  â•šâ•â•â•šâ•â•     â•šâ•â•",
]
LOGO_MEDIUM = [
    " â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•— â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•— â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•— â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•— â–ˆâ–ˆâ–ˆâ•—   â–ˆâ–ˆâ–ˆâ•—",
    " â–ˆâ–ˆâ•”â•â•â•â•â•â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—â–ˆâ–ˆâ•”â•â•â•â•â•â–ˆâ–ˆâ•”â•â•â•â•â•â•šâ•â•â–ˆâ–ˆâ•”â•â•â•â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—â–ˆâ–ˆâ•”â•â•â•â•â•â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ•— â–ˆâ–ˆâ–ˆâ–ˆâ•‘",
    " â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•”â•â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—   â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•”â•â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•‘â–ˆâ–ˆâ•”â–ˆâ–ˆâ–ˆâ–ˆâ•”â–ˆâ–ˆâ•‘",
    " â–ˆâ–ˆâ•”â•â•â•  â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—â–ˆâ–ˆâ•”â•â•â•  â•šâ•â•â•â•â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—â–ˆâ–ˆâ•”â•â•â•  â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘â•šâ–ˆâ–ˆâ•”â•â–ˆâ–ˆâ•‘",
    " â–ˆâ–ˆâ•‘     â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘ â•šâ•â• â–ˆâ–ˆâ•‘",
    " â•šâ•â•     â•šâ•â•  â•šâ•â•â•šâ•â•â•â•â•â•â•â•šâ•â•â•â•â•â•â•   â•šâ•â•   â•šâ•â•  â•šâ•â•â•šâ•â•â•â•â•â•â•â•šâ•â•  â•šâ•â•â•šâ•â•     â•šâ•â•",
]
LOGO_SMALL = [
    " â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•— â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•— â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•— â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•— ",
    " â–ˆâ–ˆâ•”â•â•â•â•â•â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—â–ˆâ–ˆâ•”â•â•â•â•â•â–ˆâ–ˆâ•”â•â•â•â•â•â•šâ•â•â–ˆâ–ˆâ•”â•â•â•â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—â–ˆâ–ˆâ•”â•â•â•â•â•â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—",
    " â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•”â•â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—   â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•”â•â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•‘",
    " â–ˆâ–ˆâ•”â•â•â•  â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—â–ˆâ–ˆâ•”â•â•â•  â•šâ•â•â•â•â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—â–ˆâ–ˆâ•”â•â•â•  â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•‘",
    " â–ˆâ–ˆâ•‘     â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘",
    " â•šâ•â•     â•šâ•â•  â•šâ•â•â•šâ•â•â•â•â•â•â•â•šâ•â•â•â•â•â•â•   â•šâ•â•   â•šâ•â•  â•šâ•â•â•šâ•â•â•â•â•â•â•â•šâ•â•  â•šâ•â•",
]
LOGO_MINI = [
    " â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•— â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•— â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—",
    " â–ˆâ–ˆâ•”â•â•â•â•â•â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—â–ˆâ–ˆâ•”â•â•â•â•â•â–ˆâ–ˆâ•”â•â•â•â•â•â•šâ•â•â–ˆâ–ˆâ•”â•â•â•â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—â–ˆâ–ˆâ•”â•â•â•â•â•",
    " â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•”â•â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—   â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•”â•â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—  ",
    " â–ˆâ–ˆâ•”â•â•â•  â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—â–ˆâ–ˆâ•”â•â•â•  â•šâ•â•â•â•â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—â–ˆâ–ˆâ•”â•â•â•  ",
    " â–ˆâ–ˆâ•‘     â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—",
    " â•šâ•â•     â•šâ•â•  â•šâ•â•â•šâ•â•â•â•â•â•â•â•šâ•â•â•â•â•â•â•   â•šâ•â•   â•šâ•â•  â•šâ•â•â•šâ•â•â•â•â•â•â•",
]

def select_logo(w):
    if w >= 100: return LOGO_LARGE
    if w >= 85: return LOGO_MEDIUM
    if w >= 70: return LOGO_SMALL
    if w >= 55: return LOGO_MINI
    return None

# â•â• ERROR CODES â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
ERR_TYPES = {400:"BADREQ",401:"AUTH",403:"FORBIDDEN",404:"NOTFOUND",
             408:"TIMEOUT",410:"GONE",428:"PRECOND",429:"RATELIMIT",
             451:"BLOCKED",500:"SERVERERR",502:"BADGATEWAY",503:"UNAVAILABLE",
             504:"GATEWAYTIMEOUT",522:"CFTIMEOUT",523:"CFUNREACH"}

def err_code(status, reason=""):
    if isinstance(status, int):
        return f"E{status}:{ERR_TYPES.get(status,'HTTPERR')}"
    r = (reason or "").lower()
    if "timeout" in r or "timed out" in r: return "ETIMEOUT"
    if "dns" in r or "resolve" in r: return "EDNS"
    if "refused" in r: return "EREFUSED"
    if "ssl" in r or "cert" in r: return "ESSL"
    return "EUNKNOWN"

def _platform_kind():
    if os.name == "nt": return "windows"
    if sys.platform == "darwin": return "macos"
    if os.path.exists("/data/data/com.termux"): return "termux"
    if "linux" in sys.platform.lower(): return "linux"
    return "unknown"

PLATFORM = _platform_kind()

@contextlib.contextmanager
def silence_stdio():
    old_out, old_err = sys.stdout, sys.stderr
    try:
        with open(os.devnull, "w", encoding="utf-8") as devnull:
            sys.stdout = devnull; sys.stderr = devnull; yield
    finally:
        sys.stdout, sys.stderr = old_out, old_err

def _restore_terminal():
    global _IN_ALT_SCREEN
    try:
        if _IN_ALT_SCREEN: sys.stdout.write("\033[?1049l")
        sys.stdout.write("\033[?25h"); sys.stdout.flush()
    except Exception: pass
    _IN_ALT_SCREEN = False

def _kill_children():
    for p in list(_SPAWNED_PROCS):
        try:
            if p.poll() is None: p.terminate()
        except Exception: pass
    _SPAWNED_PROCS.clear()

def _signal_handler(signum, frame):
    _restore_terminal(); _kill_children(); sys.exit(130)

signal.signal(signal.SIGINT, _signal_handler)
try: signal.signal(signal.SIGTERM, _signal_handler)
except Exception: pass
atexit.register(_restore_terminal); atexit.register(_kill_children)

def _all_ffmpeg_candidates():
    seen, out = set(), []
    try:
        import static_ffmpeg
        for p in static_ffmpeg.run.get_or_fetch_platform_executables_else_raise():
            if p and os.path.isfile(p):
                rp = os.path.realpath(p)
                if rp not in seen: seen.add(rp); out.append(rp)
    except Exception: pass
    for t in ("ffmpeg", "ffprobe"):
        p = shutil.which(t)
        if p and os.path.realpath(p) not in seen:
            seen.add(os.path.realpath(p)); out.append(p)
    return out

def _unblock_windows_binaries():
    if PLATFORM != "windows": return
    targets = set()
    for t in ("mpv", "vlc", "ffmpeg", "ffprobe"):
        p = shutil.which(t)
        if p: targets.add(p)
    for ff in _all_ffmpeg_candidates(): targets.add(ff)
    if not targets: return
    cmds = [f'Unblock-File -LiteralPath "{p}" -ErrorAction SilentlyContinue' for p in targets]
    try:
        subprocess.run(["powershell","-NoProfile","-ExecutionPolicy","Bypass","-Command","; ".join(cmds)],
                       capture_output=True, timeout=45)
    except Exception: pass

def _resolve_mpv_path(): return shutil.which("mpv") or "mpv"
def _resolve_vlc_path(): return shutil.which("vlc") or shutil.which("vlc.exe")

def _resolve_ffmpeg_path():
    cs = _all_ffmpeg_candidates()
    for p in cs:
        if "static_ffmpeg" not in p and ".freestream_venv" not in p:
            try:
                if subprocess.run([p,"-version"],capture_output=True,timeout=6).returncode == 0:
                    return p
            except Exception: pass
    for p in cs:
        try:
            if subprocess.run([p,"-version"],capture_output=True,timeout=6).returncode == 0:
                return p
        except Exception: pass
    return "ffmpeg"

def _mpv_launches_cleanly():
    try:
        r = subprocess.run([_resolve_mpv_path(),"--version"],capture_output=True,text=True,timeout=10)
        if r.returncode == 0 and "mpv" in (r.stdout or "").lower(): return True, "mpv verified"
        return False, err_code(0, f"exit {r.returncode}")
    except FileNotFoundError: return False, "mpv not found"
    except OSError as e:
        if getattr(e,"winerror",None) == 4551: return False, "blocked by Smart App Control"
        return False, err_code(0, str(e))
    except Exception as e: return False, err_code(0, str(e))

def open_with_default(target):
    try:
        if target.startswith("http://") or target.startswith("https://"):
            return webbrowser.open(target)
        if PLATFORM == "windows": os.startfile(target); return True
        if PLATFORM == "macos": subprocess.Popen(["open", target]); return True
        if PLATFORM == "termux": subprocess.Popen(["termux-open", target]); return True
        if shutil.which("xdg-open"): subprocess.Popen(["xdg-open", target]); return True
    except Exception: pass
    return False

def _install_player(which):
    if which == "mpv":
        if shutil.which("mpv"): return True, "already installed"
        attempts = []
        if PLATFORM == "windows":
            attempts = [["scoop","install","mpv"],
                        ["winget","install","-e","--id","mpv.net","--accept-source-agreements",
                         "--accept-package-agreements","--scope","user"]]
        elif PLATFORM == "macos":
            if shutil.which("brew"): attempts = [["brew","install","mpv"]]
        elif PLATFORM == "termux":
            attempts = [["pkg","install","-y","mpv-x"], ["pkg","install","-y","mpv"]]
        elif PLATFORM == "linux":
            for mgr, cmd in [("apt",["sudo","apt","install","-y","mpv"]),
                             ("pacman",["sudo","pacman","-S","--noconfirm","mpv"]),
                             ("dnf",["sudo","dnf","install","-y","mpv"]),
                             ("apk",["sudo","apk","add","mpv"])]:
                if shutil.which(mgr): attempts = [cmd]; break
        for cmd in attempts:
            try:
                subprocess.run(cmd, check=True, capture_output=True, timeout=300)
                if shutil.which("mpv"): return True, "installed"
            except Exception: continue
        return False, "failed"
    if which == "vlc":
        if _resolve_vlc_path(): return True, "already installed"
        urls = {"windows":"https://www.videolan.org/vlc/download-windows.html",
                "macos":"https://www.videolan.org/vlc/download-macosx.html",
                "linux":"https://www.videolan.org/vlc/#download"}
        url = urls.get(PLATFORM)
        if url: webbrowser.open(url); return False, f"opened {url}"
        return False, "not available"
    return False, "unknown"

def _in_venv():
    try: return Path(sys.prefix).resolve() == VENV_DIR.resolve()
    except Exception: return False

def _venv_python():
    return VENV_DIR / ("Scripts/python.exe" if PLATFORM == "windows" else "bin/python")

def _relaunch_in_venv():
    print("FreeStream Setup"); print("  Â· Preparing environment...")
    if not VENV_DIR.exists():
        try: subprocess.run([sys.executable,"-m","venv",str(VENV_DIR)],check=True)
        except subprocess.CalledProcessError:
            print("  ! venv creation failed."); sys.exit(1)
    vpy = _venv_python()
    chk = subprocess.run([str(vpy),"-c","import rich, urllib3"], capture_output=True)
    if chk.returncode != 0:
        print("  Â· Installing bootstrap libs...")
        subprocess.run([str(vpy),"-m","pip","install","--quiet","rich>=13.0","urllib3>=2.0"],check=True)
    env = dict(os.environ); env["PYTHONWARNINGS"] = "ignore"
    r = subprocess.run([str(vpy),str(SCRIPT_FILE)]+sys.argv[1:], env=env)
    sys.exit(r.returncode)

if not _in_venv(): _relaunch_in_venv()

def _deps_ready():
    if not READY_MARKER.exists(): return False
    try:
        from InquirerPy import inquirer  # noqa
        from InquirerPy.validator import EmptyInputValidator  # noqa
        from InquirerPy.utils import get_style  # noqa
        from patchright.sync_api import sync_playwright  # noqa
        import requests  # noqa
        from prompt_toolkit import Application  # noqa
        return True
    except ImportError: return False

if not _deps_ready():
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import (Progress, SpinnerColumn, TextColumn, BarColumn,
                                TaskProgressColumn, TimeElapsedColumn)
    from rich import box
    _console = Console(color_system="truecolor"); _console.clear()
    _console.print(Panel.fit(
        "ðŸ¿ [bold #00D2FF]FreeStream Setup[/bold #00D2FF]\n"
        f"[#64748B]Platform: {PLATFORM} Â· Installing...[/#64748B]",
        border_style="#3B82F6", box=box.ROUNDED))
    _console.print()
    with Progress(
        SpinnerColumn("dots", style="#00D2FF"),
        TextColumn("[bold #E2E8F0]{task.description}"),
        BarColumn(bar_width=36, style="#1E293B", complete_style="#3B82F6",
                  finished_style="#10B981", pulse_style="#3B82F6"),
        TaskProgressColumn(style="#64748B"), TimeElapsedColumn(), console=_console,
    ) as _prog:
        _t = _prog.add_task("Python packages", total=len(PYTHON_PACKAGES))
        for _pkg in PYTHON_PACKAGES:
            _n = _pkg.split(">=")[0].split("[")[0].split(",")[0]
            _prog.update(_t, description=f"Installing {_n}")
            subprocess.run([sys.executable,"-m","pip","install","--quiet",
                            "--disable-pip-version-check","--progress-bar","off",_pkg],
                           capture_output=True)
            _prog.advance(_t)
        _prog.update(_t, description="Python packages installed")
        _t = _prog.add_task("Playwright Chromium", total=1)
        try:
            subprocess.run([sys.executable,"-m","playwright","install","chromium"],
                           check=True, capture_output=True)
            _prog.update(_t, description="Playwright Chromium installed")
        except Exception: _prog.update(_t, description="Playwright Chromium skipped")
        _prog.advance(_t)
        _t = _prog.add_task("FFmpeg binary", total=1)
        try:
            subprocess.run([sys.executable,"-c","import static_ffmpeg; static_ffmpeg.add_paths()"],
                           check=True, capture_output=True)
            _prog.update(_t, description="FFmpeg installed")
        except Exception: _prog.update(_t, description="FFmpeg skipped")
        _prog.advance(_t)
        _t = _prog.add_task("MPV player", total=1)
        _ok, _msg = _install_player("mpv")
        _prog.update(_t, description=f"MPV: {_msg}"); _prog.advance(_t)
        _t = _prog.add_task("Windows trust cleanup", total=1)
        if PLATFORM == "windows": _unblock_windows_binaries()
        _prog.update(_t, description="Trust cleanup done"); _prog.advance(_t)
        _t = _prog.add_task("Verifying MPV", total=1)
        _ok, _msg = _mpv_launches_cleanly()
        _prog.update(_t, description="MPV verified" if _ok else f"MPV: {_msg}")
        _prog.advance(_t)
    READY_MARKER.touch()
    env = dict(os.environ); env["PYTHONWARNINGS"] = "ignore"
    subprocess.run([sys.executable,str(SCRIPT_FILE)]+sys.argv[1:], env=env)
    sys.exit(0)

# â•â• APP IMPORTS â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.style import Style
from rich import box
from rich.progress import (Progress as RProgress, SpinnerColumn as RSpinnerColumn,
                            TextColumn as RTextColumn, BarColumn as RBarColumn,
                            DownloadColumn, TransferSpeedColumn, TimeRemainingColumn)
from rich.live import Live as _RLive
from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator
from InquirerPy.utils import get_style
from patchright.sync_api import sync_playwright
import requests
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import (HSplit, VSplit, Window,
                                              FormattedTextControl, DynamicContainer)
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.styles import Style as PTStyle

try:
    import yt_dlp; HAS_YTDLP = True
except Exception: HAS_YTDLP = False
try:
    import static_ffmpeg; static_ffmpeg.add_paths()
except Exception: pass


console = Console(color_system="truecolor", force_terminal=True)

STYLE_PRIMARY   = "bold #00D2FF"
STYLE_SECONDARY = "bold #3B82F6"
STYLE_MUTED     = "#64748B"
STYLE_TEXT      = "#E2E8F0"
STYLE_SUCCESS   = "bold #10B981"
STYLE_WARN      = "bold #F59E0B"
STYLE_ERR       = "bold #EF4444"

BAR_STYLE    = Style(color="#1E293B")
BAR_COMPLETE = Style(color="#00D2FF")
BAR_FINISHED = Style(color="#10B981")
BAR_PULSE    = Style(color="#3B82F6")

PT_STYLE = PTStyle.from_dict({
    "title":"bold #00d2ff","list-item":"#e2e8f0",
    "list-item.selected":"bg:#3b82f6 #ffffff",
    "info-label":"#64748b","info-value":"#e2e8f0",
    "info-title":"bold #00d2ff","info-dim":"#475569 italic",
    "footer":"#475569 italic","action":"#64748b",
    "action.selected":"bg:#3b82f6 #ffffff","border":"#3b82f6",
    "status-ok":"#10b981","status-fail":"#ef4444","status-pending":"#64748b",
    "msg-warn":"#f59e0b","loading-logo":"bold #00d2ff",
    "loading-sub":"#64748b","loading-spin":"bold #3b82f6",
    "loading-hint":"#475569 italic",
})

SETTINGS_PATH = SCRIPT_DIR / "settings.json"
DEFAULT_SETTINGS = {
    "subtitle_mode":"auto","preferred_subtitle_languages":["en"],
    "block_ads":True,"max_extraction_timeout":15,"default_quality":"best",
    "require_subs":False,
    "server_mode":"auto",
    "opensubtitles_api_key":EMBEDDED_OS_API_KEY,
    "opensubtitles_username":EMBEDDED_OS_USERNAME,
    "opensubtitles_password":EMBEDDED_OS_PASSWORD,
}

def load_settings():
    if SETTINGS_PATH.exists():
        try:
            d = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
            m = {**DEFAULT_SETTINGS, **d}
            if EMBEDDED_OS_API_KEY and not m.get("opensubtitles_api_key"):
                m["opensubtitles_api_key"] = EMBEDDED_OS_API_KEY
                m["opensubtitles_username"] = EMBEDDED_OS_USERNAME
                m["opensubtitles_password"] = EMBEDDED_OS_PASSWORD
            return m
        except Exception: pass
    return dict(DEFAULT_SETTINGS)

def save_settings(s):
    try: SETTINGS_PATH.write_text(json.dumps(s, indent=2), encoding="utf-8")
    except Exception: pass

SETTINGS = load_settings()

CUSTOM_INQUIRER_STYLE = get_style(
    {"questionmark":"#00D2FF","answer":"#60A5FA","input":"#00D2FF",
     "question":"#FFFFFF","pointer":"#00D2FF","highlighted":"#00D2FF",
     "selected":"#10B981","separator":"#3B82F6","instruction":"#64748B"},
    style_override=False)

UA_DESKTOP = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

# â•â• TMDB â€” with India-block-aware fallbacks â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
TMDB_KEYS = ["b6550aa3e86008da4d00b71b435e50de",
             "90b2cae8d7161e8ba0f3836240d7d352",
             "57240db50c2008e78c261e1a934627e4",
             "8d6d91941230817f7807d643736e8a49",
             "15d2ce6757e7120038d1581ec93708a3"]

# Direct domains first, then public proxies that work when TMDB is blocked in India.
# India's government blocked api.themoviedb.org / api.tmdb.org on most ISPs (Jio/Airtel)
# in June 2024. Public Cloudflare Workers / Vercel deployments proxy the calls through
# a non-Indian edge, bypassing the DNS block.
TMDB_BASES = [
    "https://api.themoviedb.org/3",
    "https://api.tmdb.org/3",
    "https://tmdb-proxy.milindkusahu.workers.dev/3",
    "https://tmdb-api-cloudflare-proxy.vercel.app/3",
    "https://tmdb-proxy.vercel.app/3",
]

MOVIE_GENRES = {"Trending This Week":"trending","Top Rated":"top_rated",
                "Action":28,"Sci-Fi":878,"Horror":27,"Comedy":35,"Drama":18}
TV_GENRES = {"Trending TV":"trending","Top Rated":"top_rated",
             "Action":10759,"Sci-Fi":10765,"Crime":80,"Drama":18}
ANIME_GENRES = {"Trending Anime":"trending_anime","Top Rated Anime":"top_anime",
                "Anime Movies":"anime_movies",
                "Action & Shounen":10759,"Fantasy & Isekai":10765,
                "Romance & Slice of Life":"romance_slice"}

# â•â• MOVIE / TV PROVIDERS â€” vidsrc family + vidfast + peachify â•â•â•â•â•â•â•â•â•â•
# vidsrc domains resolved via vidsrc-dlp (pure HTTP 4-hop chain).
# vidfast.pro emits m3u8 directly (browser catch).
# peachify requires external AES-256-GCM decrypt; kept as last-resort.
PROVIDERS = [
    ("vidsrc.to",
     lambda k,i,s,e: f"https://vidsrc.to/embed/movie/{i}" if k=="movie" else f"https://vidsrc.to/embed/tv/{i}/{s}/{e}",
     None),
    ("vidsrc.net",
     lambda k,i,s,e: f"https://vidsrc.net/embed/movie?tmdb={i}" if k=="movie" else f"https://vidsrc.net/embed/tv?tmdb={i}&season={s}&episode={e}",
     lambda k,i,s,e: f"https://vidsrc.net/embed/movie?imdb={i}" if k=="movie" else f"https://vidsrc.net/embed/tv?imdb={i}&season={s}&episode={e}"),
    ("vidsrc.me",
     lambda k,i,s,e: f"https://vidsrc.me/embed/movie?tmdb={i}" if k=="movie" else f"https://vidsrc.me/embed/tv?tmdb={i}&season={s}&episode={e}",
     None),
    ("vidsrc-embed.ru",
     lambda k,i,s,e: f"https://vidsrc-embed.ru/embed/movie/{i}" if k=="movie" else f"https://vidsrc-embed.ru/embed/tv/{i}/{s}/{e}",
     None),
    ("peachify",
     lambda k,i,s,e: f"https://peachify.top/embed/movie/{i}" if k=="movie" else f"https://peachify.top/embed/tv/{i}/{s}/{e}",
     None),
    ("vidcore",
     lambda k,i,s,e: f"https://vidcore.net/embed/movie/{i}" if k=="movie" else f"https://vidcore.net/embed/tv/{i}/{s}/{e}",
     None),
    ("vidup",
     lambda k,i,s,e: f"https://vidup.to/embed/movie/{i}" if k=="movie" else f"https://vidup.to/embed/tv/{i}/{s}/{e}",
     None),
    ("vidnest",
     lambda k,i,s,e: f"https://vidnest.fun/embed/movie/{i}" if k=="movie" else f"https://vidnest.fun/embed/tv/{i}/{s}/{e}",
     None),
    ("vidrock",
     lambda k,i,s,e: f"https://vidrock.net/embed/movie/{i}" if k=="movie" else f"https://vidrock.net/embed/tv/{i}/{s}/{e}",
     None),
    ("vidrift",
     lambda k,i,s,e: f"https://vidrift.com/embed/movie/{i}" if k=="movie" else f"https://vidrift.com/embed/tv/{i}/{s}/{e}",
     None),
    ("vidzee",
     lambda k,i,s,e: f"https://vidzee.nu/embed/movie/{i}" if k=="movie" else f"https://vidzee.nu/embed/tv/{i}/{s}/{e}",
     None),
    ("autoembed",
     lambda k,i,s,e: f"https://player.autoembed.cc/embed/movie/{i}" if k=="movie" else f"https://player.autoembed.cc/embed/tv/{i}/{s}/{e}",
     None),
    ("multiembed",
     lambda k,i,s,e: f"https://multiembed.mov/directstream.php?video_id={i}&tmdb=1" if k=="movie" else f"https://multiembed.mov/directstream.php?video_id={i}&tmdb=1&s={s}&e={e}",
     None),
    ("nontongo",
     lambda k,i,s,e: f"https://www.nontongo.win/embed/movie/{i}" if k=="movie" else f"https://www.nontongo.win/embed/tv/{i}/{s}/{e}",
     None),
    ("smashystream",
     lambda k,i,s,e: f"https://embed.smashystream.com/playere.php?tmdb={i}" if k=="movie" else f"https://embed.smashystream.com/playere.php?tmdb={i}&season={s}&episode={e}",
     None),
    ("embed.su",
     lambda k,i,s,e: f"https://embed.su/embed/movie/{i}" if k=="movie" else f"https://embed.su/embed/tv/{i}/{s}/{e}",
     None),
]

# â•â• ANIME PROVIDERS â€” hianime + animepahe only â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
ANIKOTO_BASE = "https://anikotoapi.fampep.workers.dev"

def _anikoto_search(query):
    try:
        r = requests.get(f"{ANIKOTO_BASE}/anime/search",
                         params={"q": query}, timeout=12, verify=False)
        if r.status_code == 200:
            data = r.json() or {}
            results = data.get("results") or data.get("data") or []
            out = []
            for a in results[:25]:
                aid = a.get("id") or a.get("slug")
                title = a.get("title") or a.get("name") or "?"
                if aid: out.append({"id": str(aid), "title": title, "backend": "anikoto"})
            return out
    except Exception: pass
    return []

def _anikoto_episodes(anime_id):
    try:
        r = requests.get(f"{ANIKOTO_BASE}/anime/episodes",
                         params={"id": anime_id}, timeout=12, verify=False)
        if r.status_code == 200:
            data = r.json() or {}
            eps = data.get("episodes") or data.get("data") or []
            out = []
            for e in eps:
                eid = e.get("id") or e.get("episodeId")
                num = e.get("number") or e.get("episode") or 1
                if eid: out.append({"id": str(eid), "number": int(num)})
            return out
    except Exception: pass
    return []

def _anikoto_stream(episode_id):
    try:
        r = requests.get(f"{ANIKOTO_BASE}/anime/watch",
                         params={"id": episode_id}, timeout=15, verify=False)
        if r.status_code == 200:
            data = r.json() or {}
            sources = data.get("sources") or data.get("streams") or []
            best = None
            for s in sources:
                u = s.get("url") or s.get("file") or ""
                if ".m3u8" in u.lower(): best = u; break
            if not best and sources: best = sources[0].get("url") or sources[0].get("file")
            if best:
                h = data.get("headers") or {}
                h.setdefault("User-Agent", UA_DESKTOP)
                return best, h
    except Exception: pass
    return None, None

ALLANIME_BASE = "https://api.allanime.day/api"

def _allanime_search(query):
    gql = 'query ($search: SearchInput) { shows(search: $search, limit: 20, page: 1) { edges { _id name englishName } } }'
    try:
        r = requests.post(ALLANIME_BASE,
            headers={"User-Agent": UA_DESKTOP, "Content-Type": "application/json",
                     "Referer": "https://allanime.to/"},
            json={"query": gql, "variables": {"search": {"allowAdult": False, "query": query}}},
            timeout=12, verify=False)
        if r.status_code == 200:
            edges = ((r.json() or {}).get("data") or {}).get("shows", {}).get("edges") or []
            return [{"id": e.get("_id"), "title": e.get("englishName") or e.get("name") or "?",
                     "backend": "allanime"} for e in edges if e.get("_id")]
    except Exception: pass
    return []

def _allanime_episodes(show_id):
    gql = 'query ($showId: String!) { show(_id: $showId) { _id availableEpisodesDetail } }'
    try:
        r = requests.post(ALLANIME_BASE,
            headers={"User-Agent": UA_DESKTOP, "Content-Type": "application/json",
                     "Referer": "https://allanime.to/"},
            json={"query": gql, "variables": {"showId": show_id}},
            timeout=12, verify=False)
        if r.status_code == 200:
            detail = ((r.json() or {}).get("data") or {}).get("show", {}).get("availableEpisodesDetail") or {}
            subs = detail.get("sub") or []
            return [{"id": f"{show_id}|{n}", "number": int(n)} for n in subs if str(n).isdigit()]
    except Exception: pass
    return []

def _allanime_stream(composite_id):
    try:
        show_id, ep = composite_id.split("|")
        gql = 'query ($showId: String!, $episodeString: String!) { episode(showId: $showId, episodeString: $episodeString) { episodeString sourceUrls } }'
        r = requests.post(ALLANIME_BASE,
            headers={"User-Agent": UA_DESKTOP, "Content-Type": "application/json",
                     "Referer": "https://allanime.to/"},
            json={"query": gql, "variables": {"showId": show_id, "episodeString": str(ep)}},
            timeout=15, verify=False)
        if r.status_code == 200:
            data = r.json() or {}
            srcs = ((data.get("data") or {}).get("episode") or {}).get("sourceUrls") or []
            if not srcs: return None, None
            m3u8 = [s for s in srcs if ".m3u8" in (s.get("sourceUrl") or "")]
            pick = (m3u8 or srcs)[0]
            url = pick.get("sourceUrl") or ""
            if url.startswith("--"): url = "https://" + url[2:]
            if url.startswith("http"):
                return url, {"User-Agent": UA_DESKTOP, "Referer": "https://allanime.to/"}
    except Exception: pass
    return None, None

ANIME_PROVIDERS = ["anikoto", "allanime"]

def anime_search(query, provider="anikoto"):
    if provider == "anikoto":
        r = _anikoto_search(query)
        if r: return r
        return _allanime_search(query)
    if provider == "allanime":
        return _allanime_search(query)
    return []

def anime_info(anime_id, provider="anikoto"):
    if provider == "anikoto":
        eps = _anikoto_episodes(anime_id)
        if eps: return {"episodes": eps}
        return {"episodes": _allanime_episodes(anime_id)}
    if provider == "allanime":
        eps = _allanime_episodes(anime_id)
        if eps: return {"episodes": eps}
    return None

def anime_stream(episode_id, provider="anikoto"):
    if provider == "anikoto":
        r = _anikoto_stream(episode_id)
        if r[0]: return r
        return _allanime_stream(episode_id)
    if provider == "allanime":
        return _allanime_stream(episode_id)
    return None, None

def anime_provider_list(kind, tmdb_id, season=1, episode=1):
    return [(p, ("anime", p)) for p in ANIME_PROVIDERS]
BLOCKED_DOMAINS = [
    "googlesyndication","doubleclick","adsbygoogle","googleadservices",
    "googletagmanager","google-analytics","googletagservices",
    "popads","popcash","propellerads","adsterra","hilltopads","clickadu",
    "exoclick","juicyads","trafficjunky","trafficstars","popmyads",
    "onclickads","adf.ly","shorte.st","ouo.io","linkvertise","adfoc.us",
    "mgid.com","revcontent","taboola","outbrain","criteo","quantserve",
    "scorecardresearch","krxd.net","rlcdn.com","rubiconproject","pubmatic",
    "openx.net","indexexchange","sovrn","bidswitch","1rx.io","zonora",
    "moonbit","popunder","popuptraffic","adcash",
    "bet365","1xbet","betway","bwin","williamhill","pokerstars",
    "draftkings","fanduel","betfair","unibet","betmgm","sportsbet",
    "bovada","mybookie","casino","gambling","betting","poker",
    "roulette","jackpot","lottery","slots","leovegas",
    "facebook.net","hotjar","mixpanel","segment.io","amplitude",
    "newrelic","sentry.io","bugsnag","coinhive","crypto-loot","coinpot",
]

YTDLP_BLOCKED_HOSTS = {
    "vidsrc.mov","vidsrc.fyi","vidsrc.cc","vidsrc.pm","vidsrc.net",
    "vidsrc.xyz","vidsrc.in","vidsrc.to","vidsrc.me","vidsrc.rip",
    "vidsrc.icu","vidsrc.stream","vidsrc.vc",
    "vidrock.net","vidnest.fun","vidking.net","vidlink.pro",
    "vidfast.pro","vidfast.vc","vidup.to","videasy.net","111movies.com",
    "2embed.cc","2embed.skin","2embed.to",
    "multiembed.mov","superflixapi.top","peachify.top","uwu.peachify.top",
    "eat-peach.sbs","autoembed.cc","player.autoembed.cc","autoembed.co",
    "nontongo.win","moviesapi.to","smashystream","player.smashy.stream",
    "vidrift.com","player.vidzee.wtf","trendimovies.com","embedmaster.link",
}
DEMO_URL_PATTERNS = ("demo","placeholder","sample","test.mp4","bigbuckbunny")
IMAGE_EXTS = ('.png','.jpg','.jpeg','.gif','.webp','.bmp','.svg')

def _is_ytdlp_blocked(url):
    try:
        host = urlparse(url).hostname or ""
        return any(h in host for h in YTDLP_BLOCKED_HOSTS)
    except Exception: return False

def normalize_headers(h):
    out = {}
    if not h: return out
    for k, v in h.items():
        if not k or v is None: continue
        kl = str(k).lower().strip()
        if not kl or kl.startswith(":"): continue
        vs = str(v).strip().replace("\r","").replace("\n","")
        if vs and kl not in out: out[kl] = vs
    return out

def headers_with_fallbacks(h, referer=None):
    n = normalize_headers(h)
    if "user-agent" not in n: n["user-agent"] = UA_DESKTOP
    if referer and "referer" not in n: n["referer"] = referer
    return n

def build_ffmpeg_header_arg(h):
    n = normalize_headers(h)
    if not n: return ""
    lines = []
    for k, v in n.items():
        if k == "user-agent": continue
        pretty = "-".join(w.capitalize() for w in k.split("-"))
        lines.append(f"{pretty}: {v}")
    return "\r\n".join(lines) + "\r\n" if lines else ""

def strip_headers_query(u):
    try:
        p = urlparse(u)
        if not p.query: return u
        q = [(k,v) for k,v in parse_qsl(p.query, keep_blank_values=True)
             if k.lower() not in ("headers",)]
        return urlunparse(p._replace(query=urlencode(q)))
    except Exception: return u

def _ensure_scheme(u):
    if not u: return u
    if u.startswith("http://") or u.startswith("https://"): return u
    return "https://" + u.lstrip("/")

def _is_demo_stream(s, embed):
    if not s: return True
    low = s.lower()
    for p in DEMO_URL_PATTERNS:
        if p in low: return True
    try:
        su, eu = urlparse(s), urlparse(embed)
        if su.hostname and eu.hostname and su.hostname == eu.hostname:
            if not any(x in su.path.lower() for x in ("/hls","/stream","/cdn",".m3u8")):
                return True
    except Exception: pass
    return False

def _decode_proxy_data(u):
    try:
        q = dict(parse_qsl(urlparse(u).query, keep_blank_values=True))
        raw = q.get("data")
        if not raw: return {}
        dec = base64.b64decode(unquote(raw)+"==").decode("utf-8", errors="replace")
        out = {}
        for chunk in dec.split("|"):
            if "=" not in chunk: continue
            k, _, v = chunk.partition("=")
            k, v = k.strip().lower(), v.strip()
            if k in ("origin","referer","user-agent") and v: out[k] = v
        return out
    except Exception: return {}

def enrich_headers_from_proxy(u, h):
    ph = _decode_proxy_data(u)
    if not ph: return h
    m = dict(h)
    for k, v in ph.items():
        if k not in m: m[k] = v
    return m

def copy_to_clipboard(text):
    try:
        if PLATFORM == "windows":
            subprocess.run(["clip"], input=text.encode("utf-16"), check=True); return True
        if PLATFORM == "macos":
            subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True); return True
        if PLATFORM == "termux":
            subprocess.run(["termux-clipboard-set"], input=text.encode("utf-8"), check=True); return True
        for tool, args in [("xclip",["xclip","-selection","clipboard"]),
                           ("xsel",["xsel","--clipboard","--input"]),
                           ("wl-copy",["wl-copy"])]:
            if shutil.which(tool):
                subprocess.run(args, input=text.encode("utf-8"), check=True); return True
    except Exception: pass
    return False

def build_filename(title, kind, year=None, season=None, episode=None):
    safe = re.sub(r'[\\/*?:"<>|]', "", title).strip()
    safe = " ".join(safe.split()) or "media"
    if kind == "tv" and season is not None and episode is not None:
        return f"{safe} - S{season:02d}E{episode:02d}.mp4"
    if year and str(year).isdigit(): return f"{safe} ({year}).mp4"
    return f"{safe}.mp4"

def analyze_stream(url, hdrs):
    result = {"has_subs": False, "max_quality": "unknown", "variants": []}
    if ".m3u8" not in url.lower(): return result
    try:
        r = requests.get(url, headers=hdrs, verify=False, timeout=6)
        if r.status_code != 200: return result
        text = r.text
        for line in text.splitlines():
            if "TYPE=SUBTITLES" in line.upper():
                result["has_subs"] = True; break
        max_h = 0
        for line in text.splitlines():
            if "EXT-X-STREAM-INF" in line:
                m = re.search(r"RESOLUTION=\d+x(\d+)", line)
                if m:
                    h = int(m.group(1))
                    if h > max_h: max_h = h
        if max_h >= 2160: result["max_quality"] = "4K"
        elif max_h >= 1440: result["max_quality"] = "1440p"
        elif max_h >= 1080: result["max_quality"] = "1080p"
        elif max_h >= 720: result["max_quality"] = "720p"
        elif max_h >= 480: result["max_quality"] = "480p"
        elif max_h > 0: result["max_quality"] = f"{max_h}p"
    except Exception: pass
    return result

# â•â• Probing â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
def _probe_stream_once(url, hdrs):
    if not url: return False, err_code(0, "empty")
    low = url.lower()
    for ext in IMAGE_EXTS:
        if low.split("?")[0].endswith(ext): return False, "IMAGE"
    for p in DEMO_URL_PATTERNS:
        if p in low: return False, "DEMO"
    if ".mp4" in low:
        try:
            r = requests.head(url, headers=hdrs, verify=False, timeout=4, allow_redirects=True)
            ct = r.headers.get("content-type","").lower()
            if ct.startswith("image/"): return False, "IMAGE"
            if r.status_code in (200,206): return True, "mp4"
            return False, err_code(r.status_code)
        except Exception as e: return False, err_code(0, str(e))
    if ".m3u8" in low:
        try:
            r = requests.get(url, headers=hdrs, verify=False, timeout=6)
            if r.status_code != 200: return False, err_code(r.status_code)
            text = r.text
            if "#EXTM3U" not in text: return False, "NOT_M3U8"
            for line in text.splitlines():
                lu = line.upper()
                if "CODECS=" in lu and any(x in lu for x in ("PNG","JPEG","JPG")):
                    return False, "IMAGE_CODEC"
            if "#EXT-X-STREAM-INF" in text:
                base = url.rsplit("/",1)[0]
                for line in text.splitlines():
                    line = line.strip()
                    if line and not line.startswith("#"):
                        v = line if line.startswith("http") else f"{base}/{line}"
                        return _probe_stream_once(v, hdrs)
            base = url.rsplit("/",1)[0]
            segments = []
            for line in text.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    segments.append(line if line.startswith("http") else f"{base}/{line}")
            if not segments: return False, "NO_SEGMENTS"
            png_hits = 0
            for seg in segments[:5]:
                try:
                    sr = requests.get(seg, headers=hdrs, verify=False, timeout=6, stream=True)
                    ch = next(sr.iter_content(16), b""); sr.close()
                    if not ch: continue
                    if ch.startswith(b"\x89PNG"): png_hits += 1; continue
                    if ch.startswith(b"\xff\xd8\xff"): png_hits += 1; continue
                    if ch.startswith(b"GIF8"): png_hits += 1; continue
                    if ch[:4] == b"RIFF" and ch[8:12] == b"WEBP": png_hits += 1; continue
                    return True, "ts"
                except Exception: continue
            if png_hits >= 3: return False, "PNG_SEG"
            return False, "NO_VIDEO_SEG"
        except Exception as e: return False, err_code(0, str(e))
    try:
        r = requests.head(url, headers=hdrs, verify=False, timeout=4, allow_redirects=True)
        ct = r.headers.get("content-type","").lower()
        if ct.startswith("image/"): return False, "IMAGE"
        if "video" in ct: return True, "video"
        if "octet-stream" in ct: return True, "binary"
        return False, err_code(r.status_code)
    except Exception as e: return False, err_code(0, str(e))

def _validate_stream(url, hdrs, attempts=2):
    last = "EUNKNOWN"
    for i in range(attempts):
        ok, err = _probe_stream_once(url, hdrs)
        if ok: return True, ""
        last = err
        if i < attempts - 1: time.sleep(0.1)
    return False, last

# â•â• TMDB with multi-base fallback â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
def robust_get(fu):
    try:
        r = requests.get(fu, headers={"User-Agent": UA_DESKTOP}, timeout=8, verify=False)
        if r.status_code == 200: return r.json(), None
        return None, err_code(r.status_code)
    except Exception as e: return None, err_code(0, str(e))

def tmdb_request(endpoint, params=None):
    if params is None: params = {}
    last = "EUNKNOWN"
    for base in TMDB_BASES:
        for key in TMDB_KEYS:
            p = dict(params); p["api_key"] = key
            req = requests.Request("GET", f"{base}/{endpoint}", params=p).prepare()
            data, err = robust_get(req.url)
            if data and isinstance(data, dict) and ("results" in data or "id" in data):
                return data, None
            last = err or last
    return None, last

def tmdb_external_ids(kind, tid):
    try:
        data, _ = tmdb_request(f"{kind}/{tid}/external_ids")
        if data: return data.get("imdb_id") or None
    except Exception: pass
    return None

def enrich_with_imdb(items):
    def _fetch(it):
        if it.get("imdb"): return
        try:
            imdb = tmdb_external_ids(it["type"], it["id"])
            if imdb: it["imdb"] = imdb
        except Exception: pass
    with cf.ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(_fetch, items))
    return items

def format_tmdb_results(items, default_type="movie"):
    try: tw = shutil.get_terminal_size().columns
    except Exception: tw = 80
    title_w = max(12, tw - 32)
    out = []
    for item in items or []:
        mt = item.get("media_type") or default_type
        if mt not in ("movie","tv"): continue
        title = item.get("title") or item.get("name") or "Unknown"
        year = (item.get("release_date") or item.get("first_air_date") or "N/A")[:4]
        rating = item.get("vote_average", 0.0)
        tid = item.get("id")
        if not tid: continue
        badge = "MOVIE" if mt == "movie" else "TV"
        t = title[:title_w]
        label = f"[{badge:<5}]  {t:<{title_w}}  ({year})  â˜… {rating:.1f}"
        out.append({"name": label, "value": {"id": tid, "imdb": None,
                    "type": mt, "title": title, "year": year, "rating": rating}})
    return out

def fetch_category(ctype, sel):
    dt = "movie" if ctype == "movie" else "tv"
    p = {}
    if sel in ("trending","top_rated"):
        endpoint = (f"trending/{dt}/week" if sel == "trending" else f"{dt}/top_rated")
    elif ctype == "anime" and sel == "trending_anime":
        endpoint = "discover/tv"
        p = {"with_genres":"16","with_original_language":"ja","sort_by":"popularity.desc"}
    elif ctype == "anime" and sel == "top_anime":
        endpoint = "discover/tv"
        p = {"with_genres":"16","with_original_language":"ja","sort_by":"vote_average.desc","vote_count.gte":"200"}
    elif ctype == "anime" and sel == "anime_movies":
        endpoint = "discover/movie"; dt = "movie"
        p = {"with_genres":"16","with_original_language":"ja","sort_by":"popularity.desc"}
    elif ctype == "anime" and sel == "romance_slice":
        endpoint = "discover/tv"
        p = {"with_genres":"16,10749","with_original_language":"ja","sort_by":"popularity.desc"}
    else:
        endpoint = f"discover/{dt}"
        p = {"with_genres":sel,"sort_by":"popularity.desc"}
        if ctype == "anime":
            p["with_genres"] = f"16,{sel}"
            p["with_original_language"] = "ja"
    data, _ = tmdb_request(endpoint, p)
    raw = format_tmdb_results(data.get("results", []) if data else [], dt)
    items = [r["value"] for r in raw]
    enrich_with_imdb(items)
    return items

# â•â• Extraction â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
def _extract_via_ytdlp(embed_url, timeout=8):
    if not HAS_YTDLP: return None, None
    if _is_ytdlp_blocked(embed_url): return None, None
    try:
        with silence_stdio():
            opts = {"quiet": True, "no_warnings": True, "skip_download": True,
                    "format": "best[height<=1080]/best",
                    "http_headers": {"User-Agent": UA_DESKTOP, "Referer": embed_url},
                    "socket_timeout": timeout,
                    "extractor_args": {"generic": ["impersonate"]}}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(embed_url, download=False)
                if info and info.get("url"):
                    u = info["url"]
                    if not _is_demo_stream(u, embed_url):
                        h = dict(info.get("http_headers") or {})
                        h.setdefault("User-Agent", UA_DESKTOP)
                        h.setdefault("Referer", embed_url)
                        return u, h
                for f in (info or {}).get("formats", []):
                    u = f.get("url") or ""
                    if (".m3u8" in u or ".mp4" in u) and not _is_demo_stream(u, embed_url):
                        h = dict(f.get("http_headers") or {})
                        h.setdefault("User-Agent", UA_DESKTOP)
                        h.setdefault("Referer", embed_url)
                        return u, h
    except Exception: pass
    return None, None

def _resolve_vidsrc_via_dlp(tmdb_id, kind, season, episode, imdb_id=None):
    """Use vidsrc-dlp package to resolve vidsrc.to chain via pure HTTP."""
    try:
        # vidsrc-dlp exposes its resolver as a module; try both known entry points
        try:
            from vidsrc_dlp.resolver import VidSrcResolver  # type: ignore
        except Exception:
            try:
                from vidsrc_dlp import VidSrcResolver  # type: ignore
            except Exception:
                return None, None
        r = VidSrcResolver()
        # Prefer imdb if available
        vid = imdb_id or tmdb_id
        kwargs = {"type": kind, "imdb_id": imdb_id} if imdb_id else {"type": kind, "tmdb_id": tmdb_id}
        if kind == "tv":
            kwargs["season"] = season; kwargs["episode"] = episode
        try:
            result = r.resolve(**kwargs)
        except TypeError:
            result = r.resolve(vid, kind) if not imdb_id else r.resolve(imdb_id, kind, season, episode)
        if not result: return None, None
        hls = None
        headers = {"User-Agent": UA_DESKTOP, "Referer": "https://cloudnestra.com/"}
        if isinstance(result, dict):
            hls = result.get("hls_url") or result.get("url") or result.get("stream")
        elif isinstance(result, str):
            hls = result
        if hls: return hls, headers
    except Exception: pass
    return None, None

_BROWSER_JOB_Q = _queue.Queue()
_BROWSER_WORKER = None
_BROWSER_WORKER_LOCK = threading.Lock()
_PROBE_CANCEL = threading.Event()

def _reset_probe_cancel(): _PROBE_CANCEL.clear()
def _set_probe_cancel():   _PROBE_CANCEL.set()
def _is_probe_cancelled(): return _PROBE_CANCEL.is_set()

def _browser_worker_main():
    try:
        from patchright.sync_api import sync_playwright
    except Exception: return
    pw = None; browser = None
    try:
        pw = sync_playwright().start()
        launch_args = ["--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage","--autoplay-policy=no-user-gesture-required",
            "--mute-audio","--no-first-run","--no-default-browser-check",
            "--disable-features=WelcomePageOnStartup,CalculateNativeWinOcclusion",
            "--disable-backgrounding-occluded-windows","--disable-renderer-backgrounding",
            "--disable-background-timer-throttling","--disable-ipc-flooding-protection",
            "--disable-gpu","--no-sandbox",
            "--window-position=-10000,-10000","--window-size=1280,720"]
        for attempt in ({"channel":"chrome","headless":True,"args":launch_args},
                        {"headless":True,"args":launch_args}):
            try:
                browser = pw.chromium.launch(**attempt); break
            except Exception: continue
    except Exception: pass
    while True:
        job = _BROWSER_JOB_Q.get()
        if job is None: break
        embed_url, timeout, result, done = job
        if browser is None:
            result["error"] = "no browser"; done.set(); continue
        if _is_probe_cancelled():
            result["error"] = "cancelled"; done.set(); continue
        try:
            u, h = _pw_extract_job(browser, embed_url, timeout)
            result["url"] = u; result["headers"] = h
        except Exception as e:
            result["error"] = str(e)
        finally:
            done.set()
    try:
        if browser: browser.close()
    except Exception: pass
    try:
        if pw: pw.stop()
    except Exception: pass

def _ensure_browser_worker():
    global _BROWSER_WORKER
    with _BROWSER_WORKER_LOCK:
        if _BROWSER_WORKER is None or not _BROWSER_WORKER.is_alive():
            _BROWSER_WORKER = threading.Thread(target=_browser_worker_main,
                                                daemon=True, name="freestream-browser")
            _BROWSER_WORKER.start()
    return _BROWSER_WORKER

def _shutdown_browser_worker():
    try: _BROWSER_JOB_Q.put_nowait(None)
    except Exception: pass

atexit.register(_shutdown_browser_worker)

def _pw_extract_job(browser, embed_url, timeout):
    found = {"url": None, "headers": None}
    def _route(route):
        u = route.request.url.lower()
        if SETTINGS["block_ads"] and any(d in u for d in BLOCKED_DOMAINS):
            try: route.abort("blockedbyclient")
            except Exception: route.abort()
        else: route.continue_()
    ctx = browser.new_context(user_agent=UA_DESKTOP,
        viewport={"width":1280,"height":720}, locale="en-US",
        extra_http_headers={"Accept-Language":"en-US,en;q=0.9"})
    try:
        ctx.add_init_script("""
            Object.defineProperty(navigator,'webdriver',{get:()=>undefined});
            Object.defineProperty(navigator,'plugins',{get:()=>[1,2,3,4,5]});
            Object.defineProperty(navigator,'languages',{get:()=>['en-US','en']});
            window.chrome={runtime:{}};
            window.open=function(){return null;};
            window.alert=function(){};window.confirm=function(){return true;};
            const bad=/bet|casino|gambl|poker|slot|1xbet|bet365/;
            const _gc=window.location.assign.bind(window.location);
            const _gr=window.location.replace.bind(window.location);
            window.location.assign=function(u){if(!bad.test(u))_gc(u);};
            window.location.replace=function(u){if(!bad.test(u))_gr(u);};
            document.addEventListener('click',function(e){
                let el=e.target;
                while(el && el.tagName!=='A') el=el.parentElement;
                if(el && el.target==='_blank'){el.target='_self';}
            },true);
        """)
        ctx.route("**/*", _route)
        main_page = {"obj": None}
        def _on_page(new_page):
            try:
                if main_page["obj"] is None: main_page["obj"] = new_page; return
                new_page.close()
            except Exception: pass
        ctx.on("page", _on_page)
        page = ctx.new_page(); main_page["obj"] = page
        def on_req(req):
            u = req.url.lower()
            if (".m3u8" in u or ".mp4" in u) and not found["url"]:
                if not _is_demo_stream(req.url, embed_url):
                    found["url"] = req.url
                    try: found["headers"] = req.all_headers()
                    except Exception: found["headers"] = dict(req.headers)
        page.on("request", on_req)
        try:
            page.goto(embed_url, wait_until="domcontentloaded", timeout=int(timeout*1000))
        except Exception: pass
        page.wait_for_timeout(5000)
        positions = [(0.5,0.5),(0.5,0.4),(0.5,0.6),(0.3,0.5),(0.7,0.5)]
        start = time.time(); attempted = set()
        while time.time() - start < timeout and not found["url"]:
            if _is_probe_cancelled(): break
            for frame in page.frames:
                try:
                    size = frame.evaluate("""() => {
                        const b=document.body;if(!b)return null;
                        const r=b.getBoundingClientRect();
                        return {w:r.width,h:r.height};}""")
                except Exception: size = None
                if not size or size["w"] <= 0 or size["h"] <= 0: continue
                for px, py in positions:
                    key = (id(frame), px, py)
                    if key in attempted: continue
                    attempted.add(key)
                    try:
                        frame.click("body", position={"x": size["w"]*px,
                            "y": size["h"]*py}, timeout=200, force=True)
                    except Exception: pass
            try: page.mouse.click(640, 360)
            except Exception: pass
            page.wait_for_timeout(400)
    finally:
        try: ctx.close()
        except Exception: pass
    if found["url"]:
        return found["url"], headers_with_fallbacks(found["headers"], referer=embed_url)
    return None, None

def _extract_via_playwright(embed_url, timeout=15):
    if _is_probe_cancelled(): return None, None
    _ensure_browser_worker()
    result = {"url": None, "headers": None, "error": None}
    done = threading.Event()
    _BROWSER_JOB_Q.put((embed_url, timeout, result, done))
    if not done.wait(timeout=timeout+25): return None, None
    if result.get("error"): return None, None
    if result.get("url"): return result["url"], result["headers"]
    return None, None

def resolve_embed(embed_url, timeout=None, prefer_playwright=False):
    timeout = timeout or SETTINGS["max_extraction_timeout"]
    if not prefer_playwright and not _is_ytdlp_blocked(embed_url):
        u, h = _extract_via_ytdlp(embed_url, timeout=min(timeout, 6))
        if u: return u, h
    u, h = _extract_via_playwright(embed_url, timeout=timeout)
    if u: return u, h
    return None, None

def _try_movie_provider(name, tmdb_builder, imdb_builder, kind, ids, season, episode, timeout=15):
    if _is_probe_cancelled():
        return {"name": name, "fail": True, "error": "ECANCEL"}
    # vidsrc family: use vidsrc-dlp pure-HTTP resolver first
    if name.startswith("vidsrc") and ids.get("tmdb"):
        u, h = _resolve_vidsrc_via_dlp(ids.get("tmdb"), kind, season, episode,
                                        imdb_id=ids.get("imdb"))
        if u:
            ok, err = _validate_stream(u, h, attempts=2)
            if ok:
                return {"name": f"{name} (dlp)", "url": "", "stream": u, "headers": h}
    # Generic path: yt-dlp then browser
    attempts = []
    if imdb_builder and ids.get("imdb"):
        try: attempts.append(imdb_builder(kind, ids["imdb"], season, episode))
        except Exception: pass
    if tmdb_builder and ids.get("tmdb"):
        try: attempts.append(tmdb_builder(kind, ids["tmdb"], season, episode))
        except Exception: pass
    if not attempts:
        return {"name": name, "fail": True, "error": "ENO_ID"}
    last_err = "ENO_STREAM"
    for embed_url in attempts:
        s, h = resolve_embed(embed_url, timeout=timeout)
        if not s: continue
        ok, err = _validate_stream(s, h, attempts=2)
        if not ok: last_err = err; continue
        return {"name": name, "url": embed_url, "stream": s, "headers": h}
    return {"name": name, "fail": True, "error": last_err}

def _try_anime_provider(item, kind, tid, season, episode, timeout=15):
    if _is_probe_cancelled():
        return {"name": item[0], "fail": True, "error": "ECANCEL"}
    name = item[0]; tuple_val = item[1]
    if not isinstance(tuple_val, tuple):
        return {"name": name, "fail": True, "error": "EBAD_PROVIDER"}
    prov_type = tuple_val[0]
    data, _ = tmdb_request(f"{kind}/{tid}")
    if not data: return {"name": name, "fail": True, "error": "ENO_META"}
    title = data.get("title") or data.get("name") or ""
    if not title: return {"name": name, "fail": True, "error": "ENO_TITLE"}
    if prov_type == "anime":
        provider = tuple_val[1]
        results = anime_search(title, provider)
        if not results: return {"name": provider, "fail": True, "error": "ENO_SEARCH"}
        anime_id = results[0].get("id")
        if not anime_id: return {"name": provider, "fail": True, "error": "ENO_ID"}
        info = anime_info(anime_id, provider)
        if not info: return {"name": provider, "fail": True, "error": "ENO_EPS"}
        episodes = info.get("episodes") or []
        if not episodes: return {"name": provider, "fail": True, "error": "ENO_EPS"}
        ep_idx = max(0, episode - 1)
        if ep_idx >= len(episodes): ep_idx = 0
        ep = episodes[ep_idx]
        ep_id = ep.get("id")
        if not ep_id: return {"name": provider, "fail": True, "error": "ENO_EPID"}
        stream, hdrs = anime_stream(ep_id, provider)
        if not stream: return {"name": provider, "fail": True, "error": "ENO_STREAM"}
        hdrs = headers_with_fallbacks(hdrs)
        ok, err = _validate_stream(stream, hdrs, attempts=2)
        if not ok: return {"name": provider, "fail": True, "error": err}
        return {"name": f"anime/{provider}", "url": "", "stream": stream,
                "headers": hdrs, "subs": []}
    return {"name": name, "fail": True, "error": "EBAD_PROVIDER"}

def _probe_pool(providers, kind, ids, season=1, episode=1, is_anime=False,
                timeout=15, status_cb=None):
    if not providers: return None, [], []
    _reset_probe_cancel()
    workers = ANIME_PROBE_CONCURRENCY if is_anime else MOVIE_PROBE_CONCURRENCY
    def _try(item):
        if len(item) == 3 and callable(item[1]):
            name, tmdb_b, imdb_b = item
            return _try_movie_provider(name, tmdb_b, imdb_b, kind, ids,
                                        season, episode, timeout)
        return _try_anime_provider(item, kind, ids["tmdb"], season, episode, timeout)
    pool = cf.ThreadPoolExecutor(max_workers=workers)
    errors, all_fails, successes = [], [], []
    try:
        futures = {pool.submit(_try, p): p for p in providers}
        for f in cf.as_completed(futures):
            try:
                r = f.result()
                if not r: continue
                if r.get("fail"):
                    all_fails.append(f"{r['name']} [{r['error']}]")
                    errors.append(f"{r['name']} [{r['error']}]")
                    if status_cb: status_cb(r["name"], r["error"], False)
                    continue
                successes.append(r)
                if status_cb: status_cb(r["name"], "", True)
                if SETTINGS.get("server_mode","auto") == "auto":
                    _set_probe_cancel()
                    pool.shutdown(wait=False, cancel_futures=True)
                    return r, errors, all_fails
            except Exception: pass
        if successes:
            pool.shutdown(wait=False, cancel_futures=True)
            return {"_manual_list": successes}, errors, all_fails
    finally:
        try: pool.shutdown(wait=False, cancel_futures=True)
        except Exception: pass
    return None, errors, all_fails

# â•â• OpenSubtitles â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
_OS_CLIENT = None
_OS_CLIENT_LOCK = threading.Lock()
_OS_LAST_LOGIN = 0.0
_OS_DIRECT_TOKEN = None
_OS_DIRECT_TOKEN_T = 0.0
_OS_DIRECT_LOCK = threading.Lock()
_OS_DEBUG = bool(os.environ.get("FREESTREAM_DEBUG"))

def _os_log(msg):
    if _OS_DEBUG:
        try: console.print(f"[{STYLE_MUTED}][os] {msg}[/]")
        except Exception: pass

def _get_os_client():
    global _OS_CLIENT, _OS_LAST_LOGIN
    with _OS_CLIENT_LOCK:
        if _OS_CLIENT is not None: return _OS_CLIENT
        k = SETTINGS.get("opensubtitles_api_key","").strip()
        u = SETTINGS.get("opensubtitles_username","").strip()
        p = SETTINGS.get("opensubtitles_password","").strip()
        if not k: _os_log("no api key"); return None
        try:
            from opensubtitlescom import OpenSubtitles
        except Exception as e: _os_log(f"import failed: {e}"); return None
        elapsed = time.time() - _OS_LAST_LOGIN
        if elapsed < 1.1: time.sleep(1.1 - elapsed)
        for attempt in range(3):
            try:
                c = OpenSubtitles("FreeStream v1", k); c.login(u, p)
                _OS_CLIENT = c; _OS_LAST_LOGIN = time.time()
                _os_log("login ok (library)"); return c
            except Exception as e:
                msg = str(e); _OS_LAST_LOGIN = time.time()
                if "429" in msg and attempt < 2:
                    time.sleep(1.5*(attempt+1)); continue
                _os_log(f"login failed: {msg}"); return None
        return None

def _os_lib_search(**kwargs):
    c = _get_os_client()
    if not c: return []
    try: resp = c.search(**kwargs)
    except Exception as e: _os_log(f"lib search {kwargs}: {e}"); return []
    out = []
    for sub in (resp.data or [])[:10]:
        out.append({"language": getattr(sub, "language", kwargs.get("languages","en")),
                    "release": getattr(sub, "release", "unknown"),
                    "downloads": getattr(sub, "download_count", 0),
                    "raw": sub, "source": "lib"})
    _os_log(f"lib search {kwargs} â†’ {len(out)}")
    return out

def _os_lib_download(item, target):
    c = _get_os_client()
    if not c: return None
    try:
        srt = c.download_and_parse(item["raw"])
        if not _is_valid_srt(srt): return None
        Path(target).write_text(srt, encoding="utf-8")
        if Path(target).stat().st_size < 100: return None
        return target
    except Exception as e: _os_log(f"lib download: {e}"); return None

def _os_direct_login():
    global _OS_DIRECT_TOKEN, _OS_DIRECT_TOKEN_T
    with _OS_DIRECT_LOCK:
        if _OS_DIRECT_TOKEN and (time.time() - _OS_DIRECT_TOKEN_T) < 3500:
            return _OS_DIRECT_TOKEN
        k = SETTINGS.get("opensubtitles_api_key","").strip()
        u = SETTINGS.get("opensubtitles_username","").strip()
        p = SETTINGS.get("opensubtitles_password","").strip()
        if not k or not u or not p: return None
        try:
            r = requests.post("https://api.opensubtitles.com/api/v1/login",
                headers={"Api-Key": k, "Content-Type": "application/json",
                         "User-Agent": "FreeStream v1", "Accept": "application/json"},
                json={"username": u, "password": p}, timeout=15)
            if r.status_code == 200:
                tok = r.json().get("token")
                if tok:
                    _OS_DIRECT_TOKEN = tok; _OS_DIRECT_TOKEN_T = time.time()
                    _os_log("login ok (direct REST)"); return tok
            _os_log(f"direct login HTTP {r.status_code}: {r.text[:120]}")
        except Exception as e: _os_log(f"direct login exc: {e}")
        return None

def _os_direct_search(title=None, imdb_id=None, tmdb_id=None,
                      year=None, lang="en", season=None, episode=None):
    k = SETTINGS.get("opensubtitles_api_key","").strip()
    if not k: return []
    tok = _os_direct_login()
    headers = {"Api-Key": k, "User-Agent": "FreeStream v1", "Accept": "application/json"}
    if tok: headers["Authorization"] = f"Bearer {tok}"
    param_sets = []
    base = {}
    if lang: base["languages"] = lang
    if imdb_id and str(imdb_id).startswith("tt"):
        param_sets.append(dict(base, imdb_id=str(imdb_id).lstrip("t")))
    if tmdb_id:
        p = dict(base); p["tmdb_id"] = tmdb_id
        if season is not None: p["season_number"] = int(season)
        if episode is not None: p["episode_number"] = int(episode)
        param_sets.append(p); param_sets.append(dict(base, tmdb_id=tmdb_id))
    if title:
        if year and str(year).isdigit():
            param_sets.append(dict(base, query=title, year=int(year)))
        param_sets.append(dict(base, query=title))
    for params in param_sets:
        try:
            r = requests.get("https://api.opensubtitles.com/api/v1/subtitles",
                headers=headers, params=params, timeout=15)
            if r.status_code != 200: continue
            data = r.json()
            out = []
            for item in (data.get("data") or [])[:10]:
                attrs = item.get("attributes") or {}
                files = attrs.get("files") or []
                if not files: continue
                out.append({"language": attrs.get("language", lang or "?"),
                            "release": attrs.get("release", "unknown"),
                            "downloads": attrs.get("download_count", 0),
                            "file_id": files[0].get("file_id"), "source": "direct"})
            if out: return out
        except Exception: continue
    return []

def _os_direct_download(item, target):
    k = SETTINGS.get("opensubtitles_api_key","").strip()
    if not k or not item.get("file_id"): return None
    tok = _os_direct_login()
    if not tok: return None
    try:
        r = requests.post("https://api.opensubtitles.com/api/v1/download",
            headers={"Api-Key": k, "Authorization": f"Bearer {tok}",
                     "Content-Type": "application/json",
                     "User-Agent": "FreeStream v1", "Accept": "application/json"},
            json={"file_id": item["file_id"]}, timeout=15)
        if r.status_code != 200: return None
        link = r.json().get("link")
        if not link: return None
        r2 = requests.get(link, timeout=30)
        if r2.status_code != 200: return None
        text = r2.text
        if not _is_valid_srt(text): return None
        Path(target).write_text(text, encoding="utf-8")
        if Path(target).stat().st_size < 100: return None
        return target
    except Exception: return None

def fetch_subtitles(title, year, lang="en", imdb_id=None,
                    tmdb_id=None, season=None, episode=None, kind="movie"):
    subs = _os_direct_search(title=title, year=year, lang=lang, imdb_id=imdb_id,
                             tmdb_id=tmdb_id, season=season, episode=episode)
    if subs: return subs
    strats = []
    if lang:
        if imdb_id and str(imdb_id).startswith("tt"):
            strats.append({"imdb_id": str(imdb_id).lstrip("t"), "languages": lang})
        if title:
            if year and str(year).isdigit():
                strats.append({"query": title, "year": int(year), "languages": lang})
            strats.append({"query": title, "languages": lang})
        if tmdb_id: strats.append({"tmdb_id": tmdb_id, "languages": lang})
    for s in strats:
        subs = _os_lib_search(**s)
        if subs: return subs
    return []

def _is_valid_srt(t):
    if not t or len(t) < 50: return False
    if "<html" in t[:500].lower(): return False
    return "-->" in t

def download_subtitle(item, target):
    if item.get("source") == "direct" or item.get("file_id"):
        return _os_direct_download(item, target)
    return _os_lib_download(item, target)

def subtitle_flow(title, year, imdb_id=None, tmdb_id=None,
                  season=None, episode=None, kind="movie"):
    mode = SETTINGS["subtitle_mode"]
    if mode == "off": return None
    if not SETTINGS.get("opensubtitles_api_key"):
        console.print(f"[{STYLE_MUTED}]Subs: no OpenSubtitles API key[/]"); return None
    langs = SETTINGS["preferred_subtitle_languages"] or ["en"]
    with console.status("[cyan]Fetching subtitlesâ€¦[/cyan]", spinner="dots"):
        for lang in langs:
            subs = fetch_subtitles(title, year, lang, imdb_id=imdb_id,
                                   tmdb_id=tmdb_id, season=season,
                                   episode=episode, kind=kind)
            if not subs: continue
            p = SCRIPT_DIR / f"sub_{lang}.srt"
            for cand in subs[:5]:
                got = download_subtitle(cand, str(p))
                if got:
                    console.print(f"[{STYLE_SUCCESS}]âœ” Subtitles: {lang} "
                                  f"({Path(got).stat().st_size} bytes)[/]")
                    return got
        console.print(f"[{STYLE_MUTED}]No {','.join(langs)} subs â€” trying all languagesâ€¦[/]")
        all_subs = fetch_subtitles(title, year, None, imdb_id=imdb_id,
                                   tmdb_id=tmdb_id, season=season,
                                   episode=episode, kind=kind)
        if all_subs:
            for pick in all_subs[:5]:
                p = SCRIPT_DIR / f"sub_{pick.get('language', 'any')}.srt"
                got = download_subtitle(pick, str(p))
                if got:
                    console.print(f"[{STYLE_SUCCESS}]âœ” Subtitles: {pick.get('language','?')} "
                                  f"({Path(got).stat().st_size} bytes)[/]")
                    return got
        console.print(f"[{STYLE_MUTED}]Subs: none found for {title} ({year})[/]")
        return None

# â•â• Playback â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
def _mpv_sub_path(p):
    try: return str(Path(p).resolve()).replace("\\","/")
    except Exception: return str(p).replace("\\","/")

def play_with_mpv(stream_url, headers=None, title="", sub=None):
    if PLATFORM == "termux":
        if open_with_default(stream_url): return 0
    n = headers_with_fallbacks(headers)
    n = enrich_headers_from_proxy(stream_url, n)
    clean = _ensure_scheme(strip_headers_query(stream_url))
    cmd = [_resolve_mpv_path()]
    if title: cmd.append(f"--title={title}")
    cmd.append("--force-window=immediate")
    cmd.append("--msg-level=all=error,ffmpeg=no,hls=no,mov=no,demux=no")
    cmd.append("--term-status-msg=")
    cmd.append("--slang=en,en-US,en-GB,hi,ta,te,ml,kn,bn,mr")
    ua = n.get("user-agent"); ref = n.get("referer")
    if ua: cmd.append(f"--user-agent={ua}")
    if ref: cmd.append(f"--referrer={ref}")
    extras = [(k,v) for k,v in n.items() if k not in ("user-agent","referer")]
    if extras:
        pretty = [f"{'-'.join(w.capitalize() for w in k.split('-'))}: {v}" for k,v in extras]
        cmd.append(f"--http-header-fields={','.join(pretty)}")
    if HAS_YTDLP: cmd.append("--ytdl-raw-options=impersonate=chrome")
    if sub and Path(sub).exists() and Path(sub).stat().st_size > 100:
        cmd.append(f"--sub-file={_mpv_sub_path(sub)}"); cmd.append("--sid=auto")
    else: cmd.append("--sid=auto")
    cmd.append(clean)
    try:
        proc = subprocess.Popen(cmd); _SPAWNED_PROCS.append(proc)
        r = proc.wait()
        if proc in _SPAWNED_PROCS: _SPAWNED_PROCS.remove(proc)
        return r
    except OSError as e:
        if getattr(e,"winerror",None) == 4551:
            console.print(f"[{STYLE_WARN}]MPV blocked by Smart App Control[/]"); return -1
        console.print(f"[{STYLE_WARN}]MPV: {err_code(0,str(e))}[/]"); return -1
    except FileNotFoundError:
        console.print(f"[{STYLE_WARN}]MPV not found[/]"); return -1
    except Exception as e:
        console.print(f"[{STYLE_WARN}]MPV: {err_code(0,str(e))}[/]"); return -1

def play_with_vlc(stream_url, headers=None, title="", sub=None):
    vlc = _resolve_vlc_path()
    if not vlc: return -1
    n = headers_with_fallbacks(headers); n = enrich_headers_from_proxy(stream_url, n)
    clean = _ensure_scheme(strip_headers_query(stream_url))
    cmd = [vlc]
    ua = n.get("user-agent"); ref = n.get("referer")
    if ua: cmd.append(f"--http-user-agent={ua}")
    if ref: cmd.append(f"--http-referrer={ref}")
    if sub and Path(sub).exists(): cmd.append(f"--sub-file={_mpv_sub_path(sub)}")
    if title: cmd.append(f"--meta-title={title}")
    cmd.append(clean)
    try:
        proc = subprocess.Popen(cmd); _SPAWNED_PROCS.append(proc)
        r = proc.wait()
        if proc in _SPAWNED_PROCS: _SPAWNED_PROCS.remove(proc)
        return r
    except Exception as e:
        console.print(f"[{STYLE_WARN}]VLC: {err_code(0,str(e))}[/]"); return -1

def _prompt_install_player():
    opts = []
    if not shutil.which("mpv"): opts.append({"name":"Install MPV","value":"mpv"})
    if not _resolve_vlc_path(): opts.append({"name":"Download VLC","value":"vlc"})
    opts.append({"name":"Skip","value":None})
    if len(opts) == 1: return
    pick = inquirer.select("Install a player?", choices=opts,
                           style=CUSTOM_INQUIRER_STYLE).execute()
    if not pick: return
    ok, msg = _install_player(pick)
    if ok: console.print(f"[{STYLE_SUCCESS}]âœ“ {pick} installed[/]")
    else: console.print(f"[{STYLE_WARN}]âš  {pick}: {msg}[/]")
    time.sleep(1)

def open_stream_menu(stream_url, headers, title="", sub=None):
    have_mpv = bool(shutil.which("mpv")); have_vlc = bool(_resolve_vlc_path())
    choices = []
    if have_mpv: choices.append({"name":"â–¶  MPV (recommended)","value":"mpv"})
    if have_vlc: choices.append({"name":"â–¶  VLC","value":"vlc"})
    choices.append({"name":"ðŸ”— Copy link to clipboard","value":"copy"})
    if not have_mpv and not have_vlc:
        choices.append({"name":"ðŸ“¥ Install a playerâ€¦","value":"install"})
    choices.append({"name":"â† Back","value":"back"})
    pick = inquirer.select("Open with:", choices=choices,
                           style=CUSTOM_INQUIRER_STYLE).execute()
    if pick == "back": return "back"
    if pick == "install": _prompt_install_player(); return "back"
    if pick == "mpv":
        play_with_mpv(stream_url, headers, title=title, sub=sub); return "played"
    if pick == "vlc":
        play_with_vlc(stream_url, headers, title=title, sub=sub); return "played"
    if pick == "copy":
        if copy_to_clipboard(stream_url):
            console.print(f"[{STYLE_SUCCESS}]âœ“ Copied[/]")
        else: console.print(f"[{STYLE_MUTED}]{stream_url}[/]")
        time.sleep(1); return "back"
    return "back"

# â•â• Download â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
def _log_dl(tool, cmd, err_text):
    try:
        with open(DOWNLOAD_LOG, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*72}\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] {tool}\n")
            f.write(f"CMD: {' '.join(str(c) for c in cmd)}\n{'-'*72}\n")
            f.write(err_text or "(no stderr)\n")
    except Exception: pass

def _fmt_bytes(n):
    try: n = float(n or 0)
    except Exception: n = 0.0
    for unit in ("B","KB","MB","GB","TB"):
        if n < 1024: return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"

class _DownloadCancelled(Exception): pass

@contextlib.contextmanager
def _interruptible_download():
    try: old = signal.signal(signal.SIGINT, signal.default_int_handler)
    except Exception: old = None
    try: yield
    finally:
        try:
            if old is not None: signal.signal(signal.SIGINT, old)
        except Exception: pass

def _cleanup_partial(out):
    base = Path(out)
    for p in [base, base.with_suffix(base.suffix+".part"),
              base.with_suffix(base.suffix+".ytdl"),
              base.with_suffix(base.suffix+".temp"),
              base.with_suffix(base.suffix+".tmp")]:
        try:
            if p.exists(): p.unlink()
        except Exception: pass
    try:
        for p in base.parent.glob(base.stem + "*.part*"):
            try: p.unlink()
            except Exception: pass
    except Exception: pass

def _ask_cancel_confirm(partial_path):
    try:
        pick = inquirer.select("Do you really want to stop the download?",
            choices=[{"name":"ðŸ—‘  Yes â€” stop and delete the partial file","value":"stop"},
                     {"name":"â–¶  No â€” resume download","value":"resume"}],
            style=CUSTOM_INQUIRER_STYLE).execute()
        return pick or "stop"
    except Exception: return "stop"

def _dl_ytdlp(url, hdrs, out):
    footer = Text("  Press Ctrl+C to cancel download", style="#475569 italic")
    prog = RProgress(
        RSpinnerColumn("dots", style="#00D2FF"),
        RTextColumn("[bold #E2E8F0]{task.description}"),
        RTextColumn("[#3B82F6]{task.fields[done]}[/]"),
        RTextColumn("[#64748B]{task.fields[extra]}[/]"),
        console=console, transient=False,
    )
    captured = []; last_update = {"t": 0.0}
    t = prog.add_task("Preparingâ€¦", total=None, done="", extra="")
    with _RLive(Group(prog, footer), console=console, refresh_per_second=15, transient=False):
        def hook(d):
            now = time.time()
            if now - last_update["t"] < 0.25: return
            last_update["t"] = now
            st = d.get("status")
            if st == "downloading":
                dn = d.get("downloaded_bytes") or 0
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                sp = d.get("speed") or 0; eta = d.get("eta")
                if total:
                    pct = (dn/total)*100
                    done = f"{_fmt_bytes(dn)} / {_fmt_bytes(total)} ({pct:.1f}%)"
                else: done = _fmt_bytes(dn)
                parts = []
                if sp: parts.append(f"{_fmt_bytes(sp)}/s")
                if eta is not None:
                    try: parts.append(f"ETA {int(eta)}s")
                    except Exception: pass
                prog.update(t, description="Downloading", done=done, extra="  ".join(parts))
            elif st == "finished":
                prog.update(t, description="Finalizingâ€¦",
                            done=_fmt_bytes(d.get("total_bytes") or d.get("downloaded_bytes") or 0),
                            extra="merging")
        opts = {"outtmpl":out, "quiet":True, "no_warnings":True,
                "http_headers":hdrs, "concurrent_fragment_downloads":16,
                "merge_output_format":"mp4", "progress_hooks":[hook],
                "retries":10, "fragment_retries":10,
                "extractor_args":{"generic":["impersonate"]},
                "logger":type("L", (), {"debug":lambda s,m:None,"info":lambda s,m:None,
                    "warning":lambda s,m:None,"error":lambda s,m:captured.append(m)})()}
        try:
            with _interruptible_download():
                with silence_stdio():
                    with yt_dlp.YoutubeDL(opts) as ydl: ydl.download([url])
            prog.update(t, description="âœ“ Complete", done="", extra="")
            return True, ""
        except KeyboardInterrupt:
            _log_dl("yt-dlp", ["yt-dlp", url], "(user cancelled)")
            prog.update(t, description="âœ— Cancelled", done="", extra="")
            raise _DownloadCancelled()
        except Exception as e:
            err = "\n".join(captured) + "\n" + str(e)
            _log_dl("yt-dlp", ["yt-dlp", url], err)
            prog.update(t, description=f"âœ— {err_code(0,str(e))}", done="", extra="")
            return False, err

def _dl_ffmpeg(url, hdrs, out, is_hls, ffmpeg):
    footer = Text("  Press Ctrl+C to cancel download", style="#475569 italic")
    cmd = [ffmpeg]
    ua = hdrs.get("user-agent")
    if ua: cmd += ["-user_agent", ua]
    hs = build_ffmpeg_header_arg(hdrs)
    if hs: cmd += ["-headers", hs]
    cmd += ["-threads","0","-reconnect","1","-reconnect_streamed","1","-reconnect_delay_max","30"]
    if is_hls: cmd += ["-http_persistent","1","-http_multiple","1"]
    cmd += ["-i",url,"-c","copy"]
    if is_hls: cmd += ["-bsf:a","aac_adtstoasc"]
    cmd += ["-y",out]
    prog = RProgress(
        RSpinnerColumn("dots", style="#00D2FF"),
        RTextColumn("[bold #E2E8F0]{task.description}"),
        RBarColumn(bar_width=40, style=BAR_STYLE, complete_style=BAR_COMPLETE,
                   finished_style=BAR_FINISHED, pulse_style=BAR_PULSE),
        RTextColumn("[#3B82F6]{task.fields[info]}[/]"),
        RTextColumn("[#64748B]{task.fields[extra]}[/]"),
        console=console,
    )
    lines = []; p = None
    t = prog.add_task("Downloadingâ€¦", total=None, info="starting", extra="")
    with _RLive(Group(prog, footer), console=console, refresh_per_second=15, transient=False):
        try:
            with _interruptible_download():
                p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                                     stderr=subprocess.PIPE, text=True,
                                     errors="replace", bufsize=1)
                _SPAWNED_PROCS.append(p)
                dur = None; last = 0
                while True:
                    try: line = p.stderr.readline()
                    except Exception: line = ""
                    if not line and p.poll() is not None: break
                    if not line: continue
                    lines.append(line.rstrip())
                    if len(lines) > 500: lines = lines[-500:]
                    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+)", line)
                    if m and dur is None:
                        h, mm, s = map(int, m.groups()); dur = h*3600+mm*60+s
                        prog.update(t, total=dur)
                    m = re.search(r"time=(\d+):(\d+):(\d+)", line)
                    if m and dur:
                        h, mm, s = map(int, m.groups()); el = h*3600+mm*60+s
                        now = time.time()
                        if now - last > 0.25:
                            pct = (el/dur)*100 if dur else 0
                            prog.update(t, completed=el,
                                info=f"{el//60}:{el%60:02d} / {dur//60}:{dur%60:02d}  ({pct:.1f}%)")
                            last = now
                p.wait()
        except KeyboardInterrupt:
            if p is not None:
                try: p.terminate()
                except Exception: pass
                try: p.wait(timeout=3)
                except Exception:
                    try: p.kill()
                    except Exception: pass
            if p is not None and p in _SPAWNED_PROCS: _SPAWNED_PROCS.remove(p)
            _log_dl("ffmpeg", cmd, "(user cancelled)")
            prog.update(t, description="âœ— Cancelled", info="", extra="")
            raise _DownloadCancelled()
        except Exception as e:
            _log_dl("ffmpeg", cmd, str(e))
            prog.update(t, description=f"âœ— {err_code(0,str(e))}", info="", extra="")
            return False, str(e)
        if p is not None and p in _SPAWNED_PROCS: _SPAWNED_PROCS.remove(p)
        full = "\n".join(lines)
        if p is not None and p.returncode == 0:
            prog.update(t, description="âœ“ Complete", completed=dur or 1,
                        total=dur or 1, info="done", extra="")
            return True, ""
        _log_dl("ffmpeg", cmd, full)
        prog.update(t, description=f"âœ— ffmpeg exit {p.returncode if p else '?'}",
                    info="see log", extra="")
        return False, full

def _download_once(url, hdrs, out):
    ffmpeg = _resolve_ffmpeg_path()
    is_hls = ".m3u8" in url.lower()
    if is_hls:
        ok, _ = _dl_ffmpeg(url, hdrs, out, is_hls, ffmpeg)
        if ok: return True
        if HAS_YTDLP and not _is_ytdlp_blocked(url):
            ok, _ = _dl_ytdlp(url, hdrs, out)
            if ok: return True
    else:
        if HAS_YTDLP and not _is_ytdlp_blocked(url):
            ok, _ = _dl_ytdlp(url, hdrs, out)
            if ok: return True
        ok, _ = _dl_ffmpeg(url, hdrs, out, is_hls, ffmpeg)
        if ok: return True
    return False

def _download(url, hdrs, out):
    while True:
        try:
            if _download_once(url, hdrs, out): return True
            break
        except _DownloadCancelled:
            pick = _ask_cancel_confirm(out)
            if pick == "stop":
                _cleanup_partial(out)
                console.print(f"[{STYLE_MUTED}]Download stopped, partial file deleted[/]")
                return False
            console.print(f"[{STYLE_PRIMARY}]Resuming downloadâ€¦[/]")
            continue
    console.print(f"\n[{STYLE_WARN}]âš  Download failed[/]")
    console.print(f"[#64748B]Log: {DOWNLOAD_LOG}[/]")
    return False

def _default_download_dir():
    home = Path.home()
    if PLATFORM == "windows": order = [home/"Videos", home/"Desktop", home/"Downloads"]
    elif PLATFORM == "macos": order = [home/"Movies", home/"Desktop", home/"Downloads"]
    elif PLATFORM == "termux":
        order = [Path("/sdcard/Movies"), home/"storage"/"movies", home/"storage"/"downloads"]
    else: order = [home/"Videos", home/"Desktop", home/"Downloads"]
    for c in order:
        try:
            if c.exists(): return c / "FreeStream"
        except Exception: continue
    return order[0] / "FreeStream"

def download_stream(url, headers, fname):
    n = headers_with_fallbacks(headers); n = enrich_headers_from_proxy(url, n)
    clean = _ensure_scheme(strip_headers_query(url))
    outdir = _default_download_dir()
    try: outdir.mkdir(parents=True, exist_ok=True)
    except Exception: pass
    full = outdir / fname
    console.print(f"\n[{STYLE_SECONDARY}]ðŸ“¥ â†’ {full}[/]")
    return _download(clean, n, str(full))

# â•â• Layout helpers â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
def _term_dims():
    try:
        from prompt_toolkit.application import get_app
        out = getattr(get_app(), "output", None)
        if out is not None:
            s = out.get_size()
            if s.columns > 0 and s.rows > 0:
                return max(s.rows, 8), max(s.columns, 40)
    except Exception: pass
    try:
        s = shutil.get_terminal_size()
        return max(s.lines, 8), max(s.columns, 40)
    except Exception: return 24, 80

def _pane_widths(w):
    if w < 80:
        return max(20, w - 1), 0
    avail = max(20, w - 1)
    half = avail // 2
    return half, half

def _wrap_text(text, width):
    if not text: return []
    words = text.split(); lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            if cur: lines.append(cur)
            cur = w
        else: cur = (cur + " " + w) if cur else w
    if cur: lines.append(cur)
    return lines

def _start_resize_poller(app, stop_event):
    last = {"size": None}
    def poll():
        while not stop_event.is_set():
            time.sleep(0.25)
            try:
                s = shutil.get_terminal_size()
                cur = (s.lines, s.columns)
                if cur != last["size"]:
                    last["size"] = cur
                    for _ in range(3):
                        try: app.invalidate()
                        except Exception: pass
                        time.sleep(0.05)
            except Exception: break
    t = threading.Thread(target=poll, daemon=True); t.start(); return t

def _force_initial_redraw(app):
    def _fire():
        for d in (0.05, 0.15, 0.35, 0.7, 1.2):
            time.sleep(d)
            try: app.invalidate()
            except Exception: break
    threading.Thread(target=_fire, daemon=True).start()

# â•â• Panes â€” exact equal widths via Dimension.exact â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
def _exact_dim(w):
    """Return an exact-width Dimension (correct API: classmethod, not kwarg)."""
    try:
        return Dimension.exact(w)
    except Exception:
        return Dimension(min=w, max=w, preferred=w)

def show_info_with_status(info_data, items_provider_func, title_text):
    cache_state = {"statuses": [], "result": None}
    state = {"app": None}
    def render_header():
        h, w = _term_dims()
        return [("class:title", f" {title_text[:w-2]}")]
    def render_status_list():
        h, w = _term_dims()
        visible = max(3, h-6)
        left_w, _ = _pane_widths(w); left_w = max(15, left_w)
        frags = []; entries = cache_state["statuses"]
        if not entries: frags.append(("class:status-pending", "  Â· waitingâ€¦\n"))
        for name, err, ok in entries[-visible:]:
            line = f"  âœ“ {name}" if ok else f"  âœ— {name} [{err}]"
            if len(line) > left_w: line = line[:left_w-1] + "â€¦"
            cls = "class:status-ok" if ok else "class:status-fail"
            frags.append((cls, line.ljust(left_w) + "\n"))
        used = min(len(entries), visible)
        for _ in range(visible - used):
            frags.append(("class:list-item", " " * left_w + "\n"))
        return frags
    def render_info():
        h, w = _term_dims()
        _, right_w = _pane_widths(w); right_w = max(20, right_w - 2)
        frags = []
        for line in _wrap_text(f"{info_data['title']} ({info_data['year']})", right_w):
            frags.append(("class:info-title", f" {line}\n"))
        frags.append(("class:info-value", "\n"))
        fields = [("Rating", f"â˜… {info_data['rating']:.1f}/10"),
                  ("Runtime", info_data.get("runtime","")),
                  ("Genres", info_data.get("genres","")),
                  ("Director", info_data.get("director","")),
                  ("IMDB", info_data.get("imdb","")),
                  ("Cast", ", ".join(info_data.get("cast",[])))]
        for label, val in fields:
            if not val: continue
            vw = max(15, right_w - 12)
            wrapped = _wrap_text(val, vw)
            if not wrapped: continue
            frags.append(("class:info-label", f" {label:<10}"))
            frags.append(("class:info-value", f"{wrapped[0]}\n"))
            for extra in wrapped[1:]:
                frags.append(("class:info-value", f" {'':<10}{extra}\n"))
        frags.append(("class:info-label", "\n Synopsis\n"))
        ov = (info_data.get("overview") or "")[:900]
        for line in _wrap_text(ov, max(15, right_w - 3)):
            frags.append(("class:info-value", f"  {line}\n"))
        return frags
    def render_footer():
        h, w = _term_dims()
        if w < 50: return [("class:footer", " Esc cancel\n")]
        return [("class:footer", "  Loading providersâ€¦    Esc cancel\n")]
    def make_body():
        h, w = _term_dims()
        if w < 80:
            return Window(FormattedTextControl(render_status_list), wrap_lines=False)
        lw, rw = _pane_widths(w)
        return VSplit([
            Window(FormattedTextControl(render_status_list),
                   width=_exact_dim(lw), wrap_lines=False),
            Window(width=1, char="â”‚", style="class:border"),
            Window(FormattedTextControl(render_info),
                   width=_exact_dim(rw), wrap_lines=False),
        ])
    layout = Layout(HSplit([
        Window(FormattedTextControl(render_header), height=1),
        Window(height=1, char="â”€", style="class:border"),
        DynamicContainer(make_body),
        Window(height=1, char="â”€", style="class:border"),
        Window(FormattedTextControl(render_footer), height=1),
    ]))
    kb = KeyBindings()
    @kb.add("escape")
    @kb.add("q")
    def _(event): event.app.exit()
    app = Application(layout=layout, key_bindings=kb, style=PT_STYLE,
                      full_screen=True, mouse_support=False)
    state["app"] = app
    stop_ev = threading.Event()
    _start_resize_poller(app, stop_ev); _force_initial_redraw(app)
    def status_cb(name, err, ok):
        cache_state["statuses"].append((name, err, ok))
        try: app.invalidate()
        except Exception: pass
    def worker():
        try:
            r = items_provider_func(status_cb); cache_state["result"] = r
        except Exception as e: cache_state["result"] = ("error", str(e))
        try: app.invalidate()
        except Exception: pass
        time.sleep(0.15)
        try: app.exit()
        except Exception: pass
    threading.Thread(target=worker, daemon=True).start()
    try: app.run()
    finally:
        stop_ev.set()
        try: sys.stdout.write("\033[?1049h\033[H"); sys.stdout.flush()
        except Exception: pass
    return cache_state["result"]

def show_two_pane_list(items, title_text):
    cache = {}; pending = set()
    state = {"idx":0,"focus":"list","action_idx":0,"result":None,"app":None}
    ACTIONS = [("ðŸ  Home","home"),("âŒ Exit","exit")]
    def _placeholder(it):
        return {"title": it.get("title","?"), "year": it.get("year","N/A"),
                "rating": it.get("rating",0.0), "runtime":"", "genres":"",
                "director":"", "cast":[], "overview":"Loadingâ€¦",
                "imdb": it.get("imdb","")}
    def _do_fetch(it, key):
        try:
            data, _ = tmdb_request(f"{it['type']}/{it['id']}",
                                   {"append_to_response":"credits"})
            info = _placeholder(it)
            if data:
                info["rating"] = data.get("vote_average",0.0)
                info["overview"] = data.get("overview","") or "No synopsis."
                info["genres"] = ", ".join(g["name"] for g in data.get("genres",[])[:3])
                y = data.get("release_date") or data.get("first_air_date") or "N/A"
                info["year"] = y[:4]
                credits = data.get("credits",{}) or {}
                info["cast"] = [c["name"] for c in (credits.get("cast") or [])[:5]]
                dirs = [c["name"] for c in (credits.get("crew") or []) if c.get("job") == "Director"]
                info["director"] = ", ".join(dirs[:2])
                rt = data.get("runtime")
                if not rt:
                    ert = data.get("episode_run_time") or []
                    rt = ert[0] if ert else None
                if rt:
                    h, m = divmod(int(rt), 60)
                    info["runtime"] = f"{h}h {m}m" if h else f"{m}m"
            cache[key] = info
            app = state["app"]
            if app:
                try: app.invalidate()
                except Exception: pass
        except Exception:
            cache[key] = _placeholder(it)
            app = state["app"]
            if app:
                try: app.invalidate()
                except Exception: pass
    def fetch_info(it):
        key = (it["type"], it["id"])
        if key in cache: return cache[key]
        if key not in pending:
            pending.add(key)
            threading.Thread(target=_do_fetch, args=(it, key), daemon=True).start()
        return _placeholder(it)
    def prefetch_all():
        for it in items:
            key = (it["type"], it["id"])
            if key in cache or key in pending: continue
            pending.add(key)
            threading.Thread(target=_do_fetch, args=(it, key), daemon=True).start()
    threading.Thread(target=prefetch_all, daemon=True).start()
    def render_header():
        h, w = _term_dims(); return [("class:title", f" {title_text[:w-2]}")]
    def render_list():
        h, w = _term_dims()
        visible = max(3, h-6)
        left_w, _ = _pane_widths(w); left_w = max(15, left_w)
        idx = state["idx"]
        start = max(0, idx - visible//2)
        end = min(len(items), start + visible)
        if end - start < visible: start = max(0, end - visible)
        frags = []
        for i in range(start, end):
            it = items[i]
            badge = (it.get("type") or "?")[:3].upper()
            title = (it.get("title") or "?")[:max(4, left_w - 14)]
            year = it.get("year") or "?"
            label = f" [{badge}] {title} ({year})"
            if len(label) > left_w: label = label[:left_w-1] + "â€¦"
            cls = "class:list-item.selected" if i == idx else "class:list-item"
            frags.append((cls, label.ljust(left_w) + "\n"))
        used = end - start
        for _ in range(visible - used):
            frags.append(("class:list-item", " " * left_w + "\n"))
        return frags
    def render_info():
        h, w = _term_dims()
        _, right_w = _pane_widths(w); right_w = max(20, right_w - 2)
        info = fetch_info(items[state["idx"]])
        frags = []
        for line in _wrap_text(f"{info['title']} ({info['year']})", right_w):
            frags.append(("class:info-title", f" {line}\n"))
        frags.append(("class:info-value", "\n"))
        fields = [("Rating", f"â˜… {info['rating']:.1f}/10"),
                  ("Runtime", info["runtime"]), ("Genres", info["genres"]),
                  ("Director", info["director"]),
                  ("IMDB", info.get("imdb","") or ""),
                  ("Cast", ", ".join(info["cast"]))]
        for label, val in fields:
            if not val: continue
            vw = max(15, right_w - 12)
            wrapped = _wrap_text(val, vw)
            if not wrapped: continue
            frags.append(("class:info-label", f" {label:<10}"))
            frags.append(("class:info-value", f"{wrapped[0]}\n"))
            for extra in wrapped[1:]:
                frags.append(("class:info-value", f" {'':<10}{extra}\n"))
        frags.append(("class:info-label", "\n Synopsis\n"))
        ov = info["overview"][:900]
        for line in _wrap_text(ov, max(15, right_w - 3)):
            frags.append(("class:info-value", f"  {line}\n"))
        return frags
    def render_footer():
        h, w = _term_dims()
        if w < 50: return [("class:footer", " â†‘â†“ Â· Enter Â· Esc Â· â†’ ops\n")]
        if state["focus"] == "actions":
            a = state["action_idx"]
            hc = "class:action.selected" if a == 0 else "class:action"
            ec = "class:action.selected" if a == 1 else "class:action"
            return [(hc,"  Home  "),("class:footer","  "),(ec,"  Exit  "),
                    ("class:footer","      â† back   Enter activate   â†‘â†“ toggle\n")]
        return [("class:action","  Home  "),("class:footer","  "),
                ("class:action","  Exit  "),
                ("class:footer","      â†‘â†“ navigate   â†’ ops   Enter select   Esc back\n")]
    def make_body():
        h, w = _term_dims()
        if w < 80: return Window(FormattedTextControl(render_list), wrap_lines=False)
        lw, rw = _pane_widths(w)
        return VSplit([
            Window(FormattedTextControl(render_list),
                   width=_exact_dim(lw), wrap_lines=False),
            Window(width=1, char="â”‚", style="class:border"),
            Window(FormattedTextControl(render_info),
                   width=_exact_dim(rw), wrap_lines=False),
        ])
    layout = Layout(HSplit([
        Window(FormattedTextControl(render_header), height=1),
        Window(height=1, char="â”€", style="class:border"),
        DynamicContainer(make_body),
        Window(height=1, char="â”€", style="class:border"),
        Window(FormattedTextControl(render_footer), height=1),
    ]))
    kb = KeyBindings()
    @kb.add("up")
    def _(event):
        if state["focus"] == "actions": state["action_idx"] = max(0, state["action_idx"]-1)
        else: state["idx"] = max(0, state["idx"]-1)
        event.app.invalidate()
    @kb.add("down")
    def _(event):
        if state["focus"] == "actions": state["action_idx"] = min(len(ACTIONS)-1, state["action_idx"]+1)
        else: state["idx"] = min(len(items)-1, state["idx"]+1)
        event.app.invalidate()
    @kb.add("pageup")
    def _(event):
        if state["focus"] != "actions": state["idx"] = max(0, state["idx"]-10)
        event.app.invalidate()
    @kb.add("pagedown")
    def _(event):
        if state["focus"] != "actions": state["idx"] = min(len(items)-1, state["idx"]+10)
        event.app.invalidate()
    @kb.add("right")
    def _(event): state["focus"] = "actions"; event.app.invalidate()
    @kb.add("left")
    def _(event): state["focus"] = "list"; event.app.invalidate()
    @kb.add("enter")
    def _(event):
        if state["focus"] == "actions": state["result"] = ACTIONS[state["action_idx"]][1]
        else: state["result"] = ("select", state["idx"])
        event.app.exit()
    @kb.add("escape")
    @kb.add("q")
    def _(event): state["result"] = "back"; event.app.exit()
    app = Application(layout=layout, key_bindings=kb, style=PT_STYLE,
                      full_screen=True, mouse_support=False)
    state["app"] = app
    stop_ev = threading.Event()
    _start_resize_poller(app, stop_ev); _force_initial_redraw(app)
    try: app.run()
    finally:
        stop_ev.set()
        try: sys.stdout.write("\033[?1049h\033[H"); sys.stdout.flush()
        except Exception: pass
    return state["result"]

def show_loading_screen(title_text, subtitle_text="booting upâ€¦"):
    frames = ["â£¾","â£½","â£»","â¢¿","â¡¿","â£Ÿ","â£¯","â£·"]
    state = {"frame": 0, "app": None}
    def render():
        h, w = _term_dims()
        logo = select_logo(w)
        frags = []
        blank_top = max(1, (h - (len(logo) if logo else 3) - 6) // 3)
        for _ in range(blank_top): frags.append(("", "\n"))
        if logo:
            logo_w = max(len(line) for line in logo)
            pad = max(0, (w - logo_w) // 2); pad_str = " " * pad
            for line in logo:
                if w >= logo_w + 2:
                    frags.append(("class:loading-logo", pad_str + line + "\n"))
                else:
                    frags.append(("class:loading-logo", line[:w] + "\n"))
        else:
            title = " F R E E S T R E A M "
            pad = max(0, (w - len(title)) // 2)
            frags.append(("class:loading-logo", " " * pad + title + "\n"))
        frags.append(("", "\n"))
        sub = f"  {subtitle_text}  "
        sub_pad = max(0, (w - len(sub)) // 2)
        frags.append(("class:loading-sub", " " * sub_pad + sub + "\n"))
        frags.append(("", "\n"))
        spin = frames[state["frame"] % len(frames)]
        spin_line = f"  {spin}  "
        spin_pad = max(0, (w - len(spin_line)) // 2)
        frags.append(("class:loading-spin", " " * spin_pad + spin_line + "\n"))
        if h > 4:
            frags.append(("", "\n"))
            hint = "press Enter / Esc to skip"
            hint_pad = max(0, (w - len(hint)) // 2)
            frags.append(("class:loading-hint", " " * hint_pad + hint))
        return frags
    layout = Layout(HSplit([Window(FormattedTextControl(render), wrap_lines=False)]))
    kb = KeyBindings()
    @kb.add("escape")
    @kb.add("q")
    @kb.add("enter")
    def _(event): event.app.exit()
    app = Application(layout=layout, key_bindings=kb, style=PT_STYLE,
                      full_screen=True, mouse_support=False)
    state["app"] = app; _force_initial_redraw(app)
    def tick():
        while state["frame"] < 20:
            time.sleep(0.08); state["frame"] += 1
            try: app.invalidate()
            except Exception: break
        try: app.exit()
        except Exception: pass
    threading.Thread(target=tick, daemon=True).start()
    try: app.run()
    finally:
        try: sys.stdout.write("\033[?1049h\033[H"); sys.stdout.flush()
        except Exception: pass

def print_banner():
    console.clear()
    try: w = shutil.get_terminal_size().columns
    except Exception: w = 80
    logo = select_logo(w)
    if logo is None:
        title = Text("F R E E S T R E A M", style="bold #00D2FF", justify="center")
        sub = Text("Movies Â· TV Â· Anime", style=STYLE_MUTED, justify="center")
        console.print(Panel(Group(title, sub), border_style=STYLE_SECONDARY, box=box.ROUNDED))
        console.print(); return
    logo_w = max(len(line) for line in logo)
    pad = max(0, (w - logo_w) // 2); pad_str = " " * pad
    for line in logo:
        console.print(f"[bold #00D2FF]{pad_str}{line}[/]")
    console.print()
    sub = Text("Movies Â· TV Â· Anime", style=STYLE_MUTED, justify="center")
    console.print(sub)
    console.print()

def _fetch_info_dict(item):
    mt, tid = item["type"], item["id"]
    data, _ = tmdb_request(f"{mt}/{tid}", {"append_to_response":"credits"})
    imdb = item.get("imdb") or tmdb_external_ids(mt, tid)
    if not data:
        return {"title": item["title"], "year": item.get("year","N/A"),
                "rating": item.get("rating",0.0), "runtime":"", "genres":"",
                "director":"", "cast":[], "overview":"", "imdb": imdb or ""}
    info = {"title": data.get("title") or data.get("name") or item["title"],
            "year": (data.get("release_date") or data.get("first_air_date") or "N/A")[:4],
            "rating": data.get("vote_average", 0.0),
            "overview": data.get("overview","") or "No synopsis.",
            "genres": ", ".join(g["name"] for g in data.get("genres",[])[:3]),
            "director":"", "cast":[], "runtime":"", "imdb": imdb or ""}
    credits = data.get("credits",{}) or {}
    info["cast"] = [c["name"] for c in (credits.get("cast") or [])[:5]]
    dirs = [c["name"] for c in (credits.get("crew") or []) if c.get("job") == "Director"]
    info["director"] = ", ".join(dirs[:2])
    rt = data.get("runtime")
    if not rt:
        ert = data.get("episode_run_time") or []
        rt = ert[0] if ert else None
    if rt:
        h, m = divmod(int(rt), 60)
        info["runtime"] = f"{h}h {m}m" if h else f"{m}m"
    return info

def _print_stream_info(analysis):
    has_subs = analysis.get("has_subs", False)
    want_subs = SETTINGS.get("require_subs", False)
    if not want_subs or has_subs: return
    console.print(f"[{STYLE_WARN}]Note: no soft subtitles in stream â€” this is all we found[/]")

def _manual_server_pick(successes, dtitle):
    if not successes: return None
    choices = []
    for s in successes:
        q = s.get("_quality","unknown")
        label = f"{s['name']}"
        choices.append({"name": label, "value": s})
    choices.append({"name":"â† Back","value":None})
    return inquirer.select(f"Pick server for {dtitle}:", choices=choices,
                           style=CUSTOM_INQUIRER_STYLE, max_height="70%").execute()

def handle_playback(item, season=1, episode=1):
    mt, tid = item["type"], item["id"]
    title, year = item["title"], item.get("year")
    imdb = item.get("imdb") or tmdb_external_ids(mt, tid)
    is_anime = item.get("is_anime", False)
    dtitle = (f"{title} S{season:02d}E{episode:02d}" if mt == "tv" else title)
    fname = build_filename(title, mt, year=year, season=season, episode=episode)
    console.print(f"[{STYLE_PRIMARY}]Fetching info...[/]")
    info_dict = _fetch_info_dict(item)
    if is_anime:
        providers = list(PROVIDERS) + anime_provider_list(mt, tid, season, episode)
    else:
        providers = list(PROVIDERS)
    ids = {"tmdb": tid, "imdb": imdb}
    def worker(status_cb):
        r, errs, fails = _probe_pool(providers, mt, ids, season, episode,
                                      is_anime=is_anime, status_cb=status_cb)
        return (r, errs, fails)
    result = show_info_with_status(info_dict, worker,
        f"Loading Â· {dtitle}" if not is_anime else f"Anime Â· {dtitle}")
    if not result or (isinstance(result, tuple) and len(result) == 2 and result[0] == "error"):
        console.print(f"[{STYLE_ERR}]âœ— No providers[/]"); time.sleep(1.5); return
    r, errs, fails = result

    if r and isinstance(r, dict) and "_manual_list" in r:
        pick = _manual_server_pick(r["_manual_list"], dtitle)
        if not pick: return
        r = pick

    if not r:
        console.print(f"\n[{STYLE_ERR}]âœ— All servers failed[/]")
        for e in fails[:8]: console.print(f"  [#64748B]Â· {e}[/]")
        if len(fails) > 8: console.print(f"  [#64748B]Â· â€¦ and {len(fails)-8} more[/]")
        choice = inquirer.select("Options:", choices=[
            {"name":"ðŸ”„ Try Another Server","value":"retry"},
            {"name":"ðŸ  Home","value":"home"}],
            style=CUSTOM_INQUIRER_STYLE).execute()
        if choice == "retry": return handle_playback(item, season, episode)
        return

    stream, headers = r["stream"], r["headers"]
    console.print(f"\n[{STYLE_SUCCESS}]âœ“ Stream via {r['name']}[/]")
    analysis = analyze_stream(stream, headers); _print_stream_info(analysis)
    sub = subtitle_flow(title, year or "N/A", imdb_id=imdb, tmdb_id=tid,
                        season=(season if mt == "tv" else None),
                        episode=(episode if mt == "tv" else None), kind=mt)
    open_stream_menu(stream, headers, title=dtitle, sub=sub)
    cont = inquirer.select("Stream Options:", choices=[
        {"name":"ðŸ“¥ Download Video","value":"dl"},
        {"name":"ðŸ” Try Another Server","value":"retry"},
        {"name":"ðŸ  Home","value":"home"}],
        style=CUSTOM_INQUIRER_STYLE).execute()
    if cont == "dl":
        sub_choice = None
        if SETTINGS.get("opensubtitles_api_key") and SETTINGS["subtitle_mode"] != "off":
            langs_str = ", ".join(SETTINGS.get("preferred_subtitle_languages") or ["en"])
            try:
                pick = inquirer.select("Download with subtitles?",
                    choices=[{"name":f"Yes ({langs_str})","value":"y"},
                             {"name":"No","value":"n"}],
                    style=CUSTOM_INQUIRER_STYLE).execute()
                if pick == "y":
                    for lang in (SETTINGS.get("preferred_subtitle_languages") or ["en"]):
                        subs = fetch_subtitles(title, year, lang, imdb_id=imdb, tmdb_id=tid,
                                               season=(season if mt == "tv" else None),
                                               episode=(episode if mt == "tv" else None), kind=mt)
                        for cand in subs[:5]:
                            p = SCRIPT_DIR / f"sub_{lang}.srt"
                            if download_subtitle(cand, str(p)):
                                sub_choice = p; break
                        if sub_choice: break
                    if not sub_choice:
                        console.print(f"[{STYLE_MUTED}]Subs: none found for download[/]")
            except Exception: pass
        ok = download_stream(stream, headers, fname)
        if ok and sub_choice and Path(sub_choice).exists():
            outdir = _default_download_dir()
            base = Path(outdir) / Path(fname).with_suffix("")
            try:
                shutil.copy(sub_choice, Path(f"{base}.srt"))
                console.print(f"[{STYLE_SUCCESS}]âœ“ Subtitle saved next to video[/]")
            except Exception: pass
    elif cont == "retry":
        _force_manual_retry(item, season, episode)
        return

def _force_manual_retry(item, season, episode):
    mt, tid = item["type"], item["id"]
    imdb = item.get("imdb") or tmdb_external_ids(mt, tid)
    is_anime = item.get("is_anime", False)
    dtitle = (f"{item['title']} S{season:02d}E{episode:02d}" if mt == "tv" else item["title"])
    if is_anime:
        providers = list(PROVIDERS) + anime_provider_list(mt, tid, season, episode)
    else:
        providers = list(PROVIDERS)
    console.print(f"\n[{STYLE_PRIMARY}]Probing servers for manual pickâ€¦[/]")
    successes = []
    ids = {"tmdb": tid, "imdb": imdb}
    def status_cb(name, err, ok): pass
    old_mode = SETTINGS.get("server_mode","auto")
    SETTINGS["server_mode"] = "manual"
    try:
        r, errs, fails = _probe_pool(providers, mt, ids, season, episode,
                                      is_anime=is_anime, status_cb=status_cb)
    finally:
        SETTINGS["server_mode"] = old_mode
    if r and isinstance(r, dict) and "_manual_list" in r:
        successes = r["_manual_list"]
    if not successes:
        console.print(f"[{STYLE_ERR}]âœ— No servers available[/]"); time.sleep(1.5); return
    pick = _manual_server_pick(successes, dtitle)
    if not pick: return
    stream, headers = pick["stream"], pick["headers"]
    console.print(f"\n[{STYLE_SUCCESS}]âœ“ Stream via {pick['name']}[/]")
    sub = subtitle_flow(item["title"], item.get("year") or "N/A", imdb_id=imdb, tmdb_id=tid,
                        season=(season if mt == "tv" else None),
                        episode=(episode if mt == "tv" else None), kind=mt)
    open_stream_menu(stream, headers, title=dtitle, sub=sub)
    cont = inquirer.select("Stream Options:", choices=[
        {"name":"ðŸ“¥ Download Video","value":"dl"},
        {"name":"ðŸ” Try Another Server","value":"retry"},
        {"name":"ðŸ  Home","value":"home"}],
        style=CUSTOM_INQUIRER_STYLE).execute()
    if cont == "dl":
        download_stream(stream, headers,
            build_filename(item["title"], mt, year=item.get("year"),
                           season=season, episode=episode))
    elif cont == "retry":
        _force_manual_retry(item, season, episode)

def _season_episode_flow(item):
    mt, tid = item["type"], item["id"]
    data, _ = tmdb_request(f"{mt}/{tid}")
    if not data: return None
    title = data.get("title") or data.get("name") or item["title"]
    year = (data.get("release_date") or data.get("first_air_date") or "N/A")[:4]
    while True:
        seasons = [s for s in data.get("seasons",[]) if s.get("season_number",0) > 0]
        if not seasons: return None
        sc = [{"name":f"Season {s['season_number']} ({s.get('episode_count',0)} eps)",
               "value":s["season_number"]} for s in seasons]
        sc += [{"name":"ðŸ  Home","value":"__home__"},{"name":"â† Back","value":"__back__"}]
        ss = inquirer.select("Season:", choices=sc, style=CUSTOM_INQUIRER_STYLE,
                             max_height="50%").execute()
        if ss in ("__back__","__home__"): return None
        ed, _ = tmdb_request(f"tv/{tid}/season/{ss}")
        eps = ed.get("episodes",[]) if ed else []
        if not eps: continue
        ec = [{"name":f"E{e['episode_number']:02d} â€” {e.get('name','Episode')}",
               "value":e["episode_number"]} for e in eps]
        ec += [{"name":"ðŸ  Home","value":"__home__"},{"name":"â† Back","value":"__back__"}]
        se = inquirer.select("Episode:", choices=ec, style=CUSTOM_INQUIRER_STYLE,
                             max_height="50%").execute()
        if se == "__back__": continue
        if se == "__home__": return None
        return title, year, ss, se

def _tmdb_search(q, kind_override=None):
    """Search TMDB with multiple fallbacks so Indian films resolve even
    when the primary domain is blocked or the film has a native title."""
    if kind_override:
        data, _ = tmdb_request(f"search/{kind_override}", {"query":q,"include_adult":"false"})
        results = (data or {}).get("results") or []
    else:
        data, _ = tmdb_request("search/multi", {"query":q,"include_adult":"false"})
        results = (data or {}).get("results") or []
    if not results:
        m, _ = tmdb_request("search/movie", {"query":q,"include_adult":"false"})
        results = (m or {}).get("results") or []
        for r in results: r.setdefault("media_type", "movie")
    if not results:
        t, _ = tmdb_request("search/tv", {"query":q,"include_adult":"false"})
        results = (t or {}).get("results") or []
        for r in results: r.setdefault("media_type", "tv")
    if not results:
        # Indian titles sometimes only resolve when the locale is explicitly hi-IN
        m, _ = tmdb_request("search/movie",
                            {"query":q,"include_adult":"false","language":"hi-IN"})
        results = (m or {}).get("results") or []
        for r in results: r.setdefault("media_type", "movie")
    for r in results:
        if not r.get("media_type"):
            r["media_type"] = "movie" if "title" in r else "tv"
    return results

def search_flow():
    q = inquirer.text(message="Search (leave empty to go back):",
                      style=CUSTOM_INQUIRER_STYLE).execute()
    q = (q or "").strip()
    if not q: return
    console.print(f"[{STYLE_PRIMARY}]Searching...[/]")
    raw = format_tmdb_results(_tmdb_search(q))
    if not raw:
        console.print(f"[{STYLE_WARN}]No results[/]"); time.sleep(1.5); return
    items = [r["value"] for r in raw]
    for it in items: it["is_anime"] = False
    with console.status("[cyan]Fetching IMDB IDsâ€¦[/cyan]", spinner="dots"):
        enrich_with_imdb(items)
    result = show_two_pane_list(items, f"Search Â· {q}")
    if result == "home": return
    if result == "exit": sys.exit(0)
    if result == "back": return
    if isinstance(result, tuple) and result[0] == "select":
        item = items[result[1]]
        if item["type"] == "tv":
            pick = _season_episode_flow(item)
            if not pick: return
            title, year, ss, se = pick
            item.update({"title":title,"year":year})
            handle_playback(item, ss, se)
        else:
            handle_playback(item)

def browse_flow(ctype):
    while True:
        if ctype == "movie": genres = MOVIE_GENRES
        elif ctype == "tv": genres = TV_GENRES
        elif ctype == "anime": genres = ANIME_GENRES
        else: return
        gcs = [{"name":n,"value":v} for n,v in genres.items()]
        gcs += [{"name":"ðŸ  Home","value":"home"},{"name":"â† Back","value":"back"}]
        gsel = inquirer.select("Category:", choices=gcs, style=CUSTOM_INQUIRER_STYLE,
                               max_height="60%").execute()
        if gsel in ("back","home"): return
        console.print(f"[{STYLE_PRIMARY}]Fetching...[/]")
        items = fetch_category(ctype, gsel)
        if not items:
            console.print(f"[{STYLE_WARN}]No titles[/]"); time.sleep(1.5); continue
        for it in items: it["is_anime"] = (ctype == "anime")
        result = show_two_pane_list(items, f"Trending Â· {gsel}")
        if result == "home": return
        if result == "exit": sys.exit(0)
        if result == "back": continue
        if isinstance(result, tuple) and result[0] == "select":
            item = items[result[1]]
            if item["type"] == "tv":
                pick = _season_episode_flow(item)
                if not pick: return
                title, year, ss, se = pick
                item.update({"title":title,"year":year})
                handle_playback(item, ss, se)
            else:
                handle_playback(item)
            return

def _run_rerun_setup():
    console.print("[#64748B]Re-running setupâ€¦[/]")
    try:
        r = subprocess.run([sys.executable,"-m","pip","install","--quiet",
                            "--disable-pip-version-check","--upgrade",*PYTHON_PACKAGES],
                           timeout=900)
        if r.returncode == 0: console.print(f"[{STYLE_SUCCESS}]âœ“ Python packages refreshed[/]")
        else: console.print(f"[{STYLE_WARN}]âš  pip returned {r.returncode}[/]")
    except Exception as e: console.print(f"[{STYLE_WARN}]âš  pip: {e}[/]")
    try:
        subprocess.run([sys.executable,"-m","playwright","install","chromium"],
                       timeout=600, capture_output=True)
        console.print(f"[{STYLE_SUCCESS}]âœ“ Chromium refreshed[/]")
    except Exception as e: console.print(f"[{STYLE_WARN}]âš  playwright: {e}[/]")
    try:
        import static_ffmpeg; static_ffmpeg.add_paths()
        console.print(f"[{STYLE_SUCCESS}]âœ“ ffmpeg checked[/]")
    except Exception as e: console.print(f"[{STYLE_WARN}]âš  ffmpeg: {e}[/]")
    ok, msg = _mpv_launches_cleanly()
    if ok: console.print(f"[{STYLE_SUCCESS}]âœ“ MPV clean[/]")
    else: console.print(f"[{STYLE_WARN}]MPV: {msg}[/]")
    inquirer.text(message="[enter]").execute()

def settings_menu():
    while True:
        print_banner()
        req_subs = "on" if SETTINGS.get("require_subs",False) else "off"
        server_mode = SETTINGS.get("server_mode","auto")
        choice = inquirer.select("Settings:", choices=[
            {"name":f"ðŸ’¬ Subtitle Mode: {SETTINGS['subtitle_mode']}","value":"subtitle_mode"},
            {"name":f"ðŸŒ Subtitle Languages: {','.join(SETTINGS['preferred_subtitle_languages'])}",
             "value":"subs_lang"},
            {"name":f"ðŸ“ Require Soft Subs: {req_subs}","value":"req_subs"},
            {"name":f"ðŸš« Block Ads: {'on' if SETTINGS['block_ads'] else 'off'}","value":"block_ads"},
            {"name":f"ðŸ“¡ Server Selection: {server_mode}","value":"server_mode"},
            {"name":"ðŸ”§ Rerun Setup (reinstall deps + refresh binaries)","value":"rerun_setup"},
            {"name":"ðŸ›¡ï¸  Re-run Windows trust cleanup","value":"trust"},
            {"name":"ðŸ  Home","value":"home"},{"name":"â† Back","value":"back"}],
            style=CUSTOM_INQUIRER_STYLE, max_height="60%").execute()
        if choice in ("back","home"): return
        if choice == "subtitle_mode":
            opts = ["auto","manual","off"]
            SETTINGS["subtitle_mode"] = opts[(opts.index(SETTINGS["subtitle_mode"])+1)%3]
        elif choice == "subs_lang":
            langs = inquirer.text(message="Language codes (en,hi,ta,te):",
                default=",".join(SETTINGS["preferred_subtitle_languages"]),
                style=CUSTOM_INQUIRER_STYLE).execute()
            SETTINGS["preferred_subtitle_languages"] = [s.strip() for s in langs.split(",") if s.strip()]
        elif choice == "req_subs":
            SETTINGS["require_subs"] = not SETTINGS.get("require_subs", False)
        elif choice == "block_ads":
            SETTINGS["block_ads"] = not SETTINGS["block_ads"]
        elif choice == "server_mode":
            opts = ["auto","manual"]
            SETTINGS["server_mode"] = opts[(opts.index(SETTINGS.get("server_mode","auto"))+1)%2]
        elif choice == "rerun_setup": _run_rerun_setup()
        elif choice == "trust":
            if PLATFORM == "windows":
                console.print("[#64748B]Running trust cleanup...[/]")
                _unblock_windows_binaries()
                ok, msg = _mpv_launches_cleanly()
                if ok: console.print(f"[{STYLE_SUCCESS}]âœ“ MPV clean[/]")
                else: console.print(f"[{STYLE_WARN}]MPV: {msg}[/]")
                time.sleep(2)
            else: console.print("[#64748B]Not on Windows[/]"); time.sleep(1)
        save_settings(SETTINGS)

def enter_alt_screen():
    global _IN_ALT_SCREEN
    sys.stdout.write("\033[?1049h\033[H"); sys.stdout.flush()
    _IN_ALT_SCREEN = True

def exit_alt_screen():
    global _IN_ALT_SCREEN
    sys.stdout.write("\033[?1049l\033[?25h"); sys.stdout.flush()
    _IN_ALT_SCREEN = False

def main_menu():
    while True:
        print_banner()
        choice = inquirer.select("Main Menu:", choices=[
            {"name":"ðŸ” Direct Search","value":"search"},
            {"name":"ðŸŽ¬ Trending Movies","value":"movies"},
            {"name":"ðŸ“º Trending TV Shows","value":"tv"},
            {"name":"ðŸŒ¸ Trending Anime","value":"anime"},
            {"name":"âš™ï¸  Settings","value":"settings"},
            {"name":"âŒ Exit","value":"exit"}],
            style=CUSTOM_INQUIRER_STYLE).execute()
        if choice == "search": search_flow()
        elif choice == "movies": browse_flow("movie")
        elif choice == "tv": browse_flow("tv")
        elif choice == "anime": browse_flow("anime")
        elif choice == "settings": settings_menu()
        elif choice == "exit": return

def main():
    enter_alt_screen()
    try:
        show_loading_screen("FreeStream", "booting upâ€¦")
        main_menu()
    except KeyboardInterrupt: pass
    finally: exit_alt_screen()



def _check_for_updates():
    try:
        r = requests.get('https://pypi.org/pypi/freestream-cli/json', timeout=4)
        if r.status_code != 200: return
        latest = (r.json().get('info') or {}).get('version')
        if not latest or latest == FREESTREAM_VERSION: return
        console.print('[bold #F59E0B]Update available: ' + FREESTREAM_VERSION + ' -> ' + latest + '[/]')
        console.print('[#64748B]   Run: pip install --upgrade freestream[/]')
    except Exception:
        pass


def main():
    enter_alt_screen()
    try:
        _check_for_updates()
        show_loading_screen('FreeStream', 'booting up...')
        main_menu()
    except KeyboardInterrupt:
        pass
    finally:
        exit_alt_screen()

if __name__ == '__main__':
    main()
