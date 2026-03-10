from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SentimentAnalyzeRequest(BaseModel):
    """情感分析请求体。"""

    model_config = ConfigDict(str_strip_whitespace=True)

    text: str = Field(..., description="待分析文本")
    threshold: float = Field(default=0.6, description="判定阈值")

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("输入文本不能为空")
        return value.strip()

    @field_validator("threshold")
    @classmethod
    def validate_threshold(cls, value: float) -> float:
        if not 0.5 <= value <= 0.95:
            raise ValueError("阈值必须位于 0.5 到 0.95 之间")
        return value


class TokenHighlight(BaseModel):
    """高亮分词项。"""

    text: str
    tone: Literal["positive", "negative", "neutral"]


class ProbabilityPayload(BaseModel):
    """概率结果。"""

    negative: float
    positive: float


class MetricsPayload(BaseModel):
    """性能指标。"""

    duration_ms: float
    device: str


class SentimentAnalyzeResponse(BaseModel):
    """情感分析响应。"""

    label: str
    sentiment: Literal["positive", "negative", "neutral"]
    threshold: float
    probabilities: ProbabilityPayload
    highlights: list[TokenHighlight]
    metrics: MetricsPayload


class HealthResponse(BaseModel):
    """健康检查响应。"""

    status: str
    model: str
    detail: str | None = None
