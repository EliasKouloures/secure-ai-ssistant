from __future__ import annotations

from pathlib import Path

from core.config import load_config


def test_load_config_uses_meta_llama_default_model(tmp_path: Path) -> None:
    config = load_config(path=tmp_path / "missing-config.toml", env={})

    assert config.backend.model_id == "meta-llama-3.1-8b-instruct"


def test_load_config_reads_file_and_env_override(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
        [app]
        title = "Custom Title"
        bind_port = 9999
        database_path = "data/demo.db"

        [backend]
        base_url = "http://127.0.0.1:11434/v1"
        model_id = "configured-model"
        supports_vision = false
        """,
        encoding="utf-8",
    )
    config = load_config(
        config_path,
        env={
            "SEKRETARIAT_BACKEND_MODEL_ID": "env-model",
            "SEKRETARIAT_BACKEND_SUPPORTS_VISION": "true",
        },
    )

    assert config.title == "Custom Title"
    assert config.bind_port == 9999
    assert config.storage.database_path == "data/demo.db"
    assert config.backend.base_url == "http://127.0.0.1:11434/v1"
    assert config.backend.model_id == "env-model"
    assert config.backend.supports_vision is True
