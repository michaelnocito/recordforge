"""pywebview API bridge for the RecordForge desktop UI.

Preserves the exact JSON contract from v1:
  generate() → {"success": True, "files": list[str], "folder": str}
             or {"success": False, "error": str, "files": []}
"""

import json as _json
import os
import subprocess
import sys
import urllib.request as _urlreq
import webbrowser
from pathlib import Path

import webview

import recordforge as rf
from recordforge import __version__
from recordforge.generators.data import DATA_REGISTRY
from recordforge.generators.documents import DOCUMENT_REGISTRY

RELEASES_URL = "https://github.com/michaelnocito/recordforge/releases/latest"
API_URL = "https://api.github.com/repos/michaelnocito/recordforge/releases/latest"


def ui_html_path() -> Path:
    """Absolute path to the wizard HTML (recordforge/ui/ui.html).

    Resolved from this package module, not the entry script: inside a PyInstaller
    onefile bundle the entry script's __file__ is flattened to the bundle root,
    but a package module keeps its recordforge/ui/ path, so this locates the
    bundled ui.html correctly both from source and when frozen.
    """
    return Path(__file__).parent / "ui.html"


def _parse_version(v: str) -> tuple[int, ...]:
    """Parse a version string into comparable integer parts.

    Strips a leading 'v' and any pre-release/build suffix (e.g. '2.1.0-rc1'),
    and treats non-numeric parts as 0 so a malformed tag never crashes the
    comparison.
    """
    core = str(v).strip().lstrip("v").split("-")[0].split("+")[0]
    parts: list[int] = []
    for piece in core.split("."):
        parts.append(int(piece) if piece.isdigit() else 0)
    return tuple(parts)


def _fetch_latest_release() -> dict:
    """Fetch the latest release JSON from the GitHub API. Raises on any failure.

    This is the ONLY network request RecordForge makes, and it runs only when
    the user clicks Check for Updates (never at startup, never automatically).
    """
    req = _urlreq.Request(
        API_URL,
        headers={
            "User-Agent": f"RecordForge/{__version__}",
            "Accept": "application/vnd.github+json",
        },
    )
    with _urlreq.urlopen(req, timeout=8) as resp:
        return _json.loads(resp.read().decode("utf-8"))


def sanitize_filename(s: str) -> str:
    """Preserve v1 sanitize_filename behavior exactly."""
    s = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in str(s).strip())
    return s[:100] or "output"


def open_path(path: str) -> bool:
    """Open a file or folder using the OS default handler. Preserve v1 logic exactly."""
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        return True
    except Exception:
        return False


class API:
    def choose_folder(self) -> str | None:
        """Open a folder picker using pywebview's native dialog (avoids tkinter/WebView2 conflict)."""
        windows = webview.windows
        if not windows:
            return None
        result = windows[0].create_file_dialog(webview.FOLDER_DIALOG)
        if result:
            return result[0]
        return None

    def open_path(self, path: str) -> bool:
        """Open a file with its default OS handler."""
        return open_path(path)

    def open_folder(self, path: str) -> bool:
        """Open a folder in the OS file explorer."""
        return open_path(path)

    def app_version(self) -> str:
        """Return the installed RecordForge version. No network call."""
        return __version__

    def open_releases(self) -> bool:
        """Hand the GitHub Releases URL to the OS browser.

        The app makes no network request itself — the browser does, the
        same as the user clicking a hyperlink.
        """
        try:
            webbrowser.open(RELEASES_URL)
            return True
        except Exception:
            return False

    def check_update(self) -> dict:
        """Opt-in version check. Runs ONLY when the user clicks Check for Updates.

        This is the single point where RecordForge itself reaches the network,
        and only on an explicit click — never at startup, never automatically.
        It asks the GitHub Releases API for the latest tag and compares it to the
        running version. Returns a small status dict for the UI:

          {"status": "latest",    "current": v, "latest": v, "url": ...}
          {"status": "available", "current": v, "latest": newer, "url": ...}
          {"status": "error",     "current": v, "message": str, "url": ...}

        Any failure (offline, rate limit, bad response) returns 'error' with a
        friendly message and never raises, so the button is always safe to click.
        """
        current = __version__
        try:
            data = _fetch_latest_release()
        except Exception:
            return {
                "status": "error",
                "current": current,
                "message": "Couldn't reach GitHub (are you offline?).",
                "url": RELEASES_URL,
            }

        latest = str(data.get("tag_name") or "").strip().lstrip("v")
        url = data.get("html_url") or RELEASES_URL
        if latest and _parse_version(latest) > _parse_version(current):
            return {"status": "available", "current": current, "latest": latest, "url": url}
        return {"status": "latest", "current": current, "latest": latest or current, "url": url}

    def generate(self, payload: dict) -> dict:
        """Generate files from the UI wizard payload.

        Returns {"success": True, "files": [...], "folder": str}
             or {"success": False, "error": str, "files": []}
        """
        try:
            mode = payload.get("mode", "documents")
            selected = payload.get("docTypes", [])
            qty = max(1, int(payload.get("quantity", 1)))
            fmt = (payload.get("format") or "").lower().strip()
            data_fmt = (payload.get("dataFormat") or "xlsx").lower().strip()
            rows = max(1, int(payload.get("rows", 50)))
            dirty = payload.get("dirty") or None
            seed = payload.get("seed")
            out_folder = (
                payload.get("outputFolder")
                or str(Path.home() / "Documents" / "recordforge")
            )

            if out_folder.startswith("~/"):
                out_folder = str(Path.home() / out_folder[2:])

            out_dir = Path(out_folder)
            out_dir.mkdir(parents=True, exist_ok=True)

            # Seed once for the whole batch so output is deterministic yet varied
            # across types and files (re-seeding per generate() call would make
            # them collide). Individual generate() calls keep seed=None.
            if seed is not None and str(seed).strip() != "":
                rf.set_seed(int(seed))

            doc_keys = [t for t in selected if t in DOCUMENT_REGISTRY]
            data_keys = [t for t in selected if t in DATA_REGISTRY]
            wants_docs = mode in ("documents", "both")
            wants_data = mode in ("data", "both")
            generated_files: list[str] = []

            if wants_docs:
                if fmt not in {"pdf", "docx", "html"}:
                    raise ValueError("Choose a document format before generating documents.")
                for doc_type in doc_keys:
                    docs = rf.generate(type=doc_type, format=fmt, count=qty, output=out_folder)
                    generated_files.extend(str(d.path) for d in docs)

            if wants_data:
                if data_fmt not in {"xlsx", "csv", "json", "jsonl"}:
                    raise ValueError("Choose a data format (xlsx, csv, json, or jsonl).")
                for dataset in data_keys:
                    docs = rf.generate(
                        type=dataset, format=data_fmt, count=qty, output=out_folder,
                        rows=rows, dirty=dirty,
                    )
                    generated_files.extend(str(d.path) for d in docs)

            return {"success": True, "files": generated_files, "folder": str(out_dir)}

        except Exception as exc:
            return {"success": False, "error": str(exc), "files": []}
