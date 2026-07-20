"""Entry point for `python -m recordforge` — launches the desktop UI."""

import webview

from recordforge.ui.app import API, ui_html_path


def main() -> None:
    """Launch the RecordForge desktop UI via pywebview."""
    api = API()
    html = ui_html_path().read_text(encoding="utf-8")

    webview.create_window(
        "RecordForge",
        html=html,
        js_api=api,
        width=860,
        height=780,
        min_size=(700, 600),
        resizable=True,
    )
    webview.start(debug=False)


if __name__ == "__main__":
    main()
