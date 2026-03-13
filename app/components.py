from __future__ import annotations

import html
import json
from uuid import uuid4

import streamlit.components.v1 as components


def render_copy_button(label: str, value: str) -> None:
    safe_label = html.escape(label)
    safe_value = json.dumps(value)
    button_id = f"copy_{uuid4().hex}"
    components.html(
        f"""
        <button id="{button_id}" style="
            border-radius:999px;
            border:1px solid rgba(10,25,47,0.16);
            background:rgba(255,255,255,0.85);
            color:#0A192F;
            font-family:IBM Plex Sans, Segoe UI, sans-serif;
            font-size:16px;
            padding:10px 16px;
            cursor:pointer;
            width:100%;
        ">{safe_label}</button>
        <script>
        const button = document.getElementById({json.dumps(button_id)});
        button.addEventListener("click", async () => {{
          await navigator.clipboard.writeText({safe_value});
          button.textContent = "Copied";
          setTimeout(() => button.textContent = {json.dumps(safe_label)}, 1200);
        }});
        </script>
        """,
        height=56,
    )
