# Installation & Build Guide

You have four ways to get RecordForge running. Pick the one that fits
how you want to use it.

---

## Option 1 — Windows Installer (Recommended)

The fastest path. Download, click, generate. No Python on your machine.

Grab the latest installer from the [Releases page](https://github.com/michaelnocito/recordforge/releases/latest).

1. Double-click `RecordForgeSetup.exe`
2. Click **Next** through the install wizard
3. Click **Finish** — optionally launch the app immediately
4. Find **RecordForge** in your **Start Menu** or on your **Desktop**
5. To uninstall: Windows Settings → Apps → search "RecordForge" → Uninstall

You do not need Python for this path.

> **Blank white screen after launch?** Install the [Microsoft Edge WebView2 Runtime](https://developer.microsoft.com/en-us/microsoft-edge/webview2/) (free, from Microsoft) — pywebview requires it on Windows.

---

## Option 2 — Python Package (pip install)

Use this when you want the CLI, the Python API, or to read and extend
the code. Requires Python 3.11+ and pip.

```powershell
git clone https://github.com/michaelnocito/recordforge.git
cd recordforge
pip install -e .
```

**CLI:**
```
recordforge generate --type invoice --format pdf --count 5
recordforge generate --type customers --format xlsx --count 2
recordforge list-types
```

**Python API:**
```python
from recordforge import generate
docs = generate(type="invoice", format="pdf", count=3)
```

**Desktop UI:**
```
python -m recordforge
```

---

## Option 3 — Build the EXE Yourself (PyInstaller)

Want your own standalone `.exe`? From the project folder in PowerShell:

```powershell
pip install pyinstaller
python -m PyInstaller --name "RecordForge" --onefile --noconsole `
  --add-data "recordforge/ui/ui.html;recordforge/ui" `
  --add-data "recordforge/renderers/templates;recordforge/renderers/templates" `
  --exclude-module pyarrow `
  recordforge/__main__.py
```

> Use `python -m PyInstaller` not `pyinstaller` directly.
> On Windows, pip installs PyInstaller to a user AppData folder that may not be in PATH.
>
> `--exclude-module pyarrow` keeps the optional Parquet dependency out of the
> desktop build so the installer stays small. Parquet output stays available
> via `pip install "recordforge[parquet]"` and the CLI. Leave the flag in even
> if pyarrow is not installed on your build machine (it is harmless then).

Output: `dist\RecordForge.exe`

---

## Option 4 — Build the Installer Yourself (Inno Setup)

You can roll your own Windows installer:

1. Install [Inno Setup](https://jrsoftware.org/isdl.php) (free)
2. Build the EXE first using Option 3 above
3. Open Inno Setup → File → Open → select `installer.iss` from the project folder
4. Press **F9** to compile
5. Output lands in an `Output\` folder inside the project directory (check the `OutputDir` line in `installer.iss` if you moved things)
