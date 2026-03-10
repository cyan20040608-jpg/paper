from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class Settings:
    """应用配置。"""

    project_root: Path = field(default_factory=lambda: Path(__file__).resolve().parents[3])
    model_dir: Path = field(init=False)
    bert_dir: Path = field(init=False)
    default_threshold: float = field(
        default_factory=lambda: float(os.getenv("APP_DEFAULT_THRESHOLD", "0.6"))
    )
    allow_origins: list[str] = field(init=False)

    def __post_init__(self) -> None:
        model_dir = os.getenv("APP_MODEL_DIR")
        bert_dir = os.getenv("APP_BERT_DIR")
        allow_origins = os.getenv("APP_ALLOW_ORIGINS")

        self.model_dir = Path(model_dir) if model_dir else self.project_root / "model_group_a_no_cnn"
        self.bert_dir = Path(bert_dir) if bert_dir else self.project_root / "bert-base-chinese"

        if allow_origins:
            self.allow_origins = [item.strip() for item in allow_origins.split(",") if item.strip()]
        else:
            self.allow_origins = [
                "http://127.0.0.1:5173",
                "http://localhost:5173",
                "http://127.0.0.1:8080",
                "http://localhost:8080",
            ]


settings = Settings()
