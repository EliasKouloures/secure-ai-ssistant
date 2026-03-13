from __future__ import annotations

import sys

from core.config import load_config


def main() -> None:
    from streamlit.web import cli as stcli

    config = load_config()
    address = config.bind_host if config.features.enable_intranet_mode else "127.0.0.1"
    sys.argv = [
        "streamlit",
        "run",
        "app/main.py",
        "--server.address",
        address,
        "--server.port",
        str(config.bind_port),
        "--browser.gatherUsageStats",
        "false",
        "--server.headless",
        "true",
    ]
    raise SystemExit(stcli.main())
