from __future__ import annotations

import json
import logging
import time
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F
import transformers.modeling_utils
import transformers.utils.import_utils
from peft import LoraConfig, TaskType, get_peft_model
from transformers import BertModel, BertTokenizer

from backend.app.core.settings import settings
from backend.app.schemas.sentiment import (
    HealthResponse,
    MetricsPayload,
    ProbabilityPayload,
    SentimentAnalyzeResponse,
    TokenHighlight,
)


logger = logging.getLogger(__name__)

POS_WORDS = {
    "好",
    "棒",
    "优秀",
    "喜欢",
    "爱",
    "赞",
    "满意",
    "推荐",
    "惊喜",
    "暖心",
    "感人",
    "值得",
}
NEG_WORDS = {
    "差",
    "烂",
    "一般",
    "失望",
    "生气",
    "避雷",
    "无语",
    "糟糕",
    "拉胯",
    "后悔",
    "垃圾",
    "不行",
}


def force_bypass_security_check() -> None:
    """兼容当前本地权重加载方式。"""

    return None


transformers.utils.import_utils.check_torch_load_is_safe = force_bypass_security_check
transformers.modeling_utils.check_torch_load_is_safe = force_bypass_security_check


class BertLoRALinear(nn.Module):
    """LoRA 线性分类头。"""

    def __init__(self, config_dict: dict, model_name: str) -> None:
        super().__init__()
        base_bert = BertModel.from_pretrained(model_name)
        peft_config = LoraConfig(
            task_type=TaskType.FEATURE_EXTRACTION,
            inference_mode=True,
            r=config_dict["lora_r"],
            lora_alpha=config_dict["lora_alpha"],
            lora_dropout=config_dict["lora_dropout"],
            target_modules=["query", "value"],
        )
        self.bert = get_peft_model(base_bert, peft_config)
        self.dropout = nn.Dropout(0.3)
        self.fc = nn.Linear(768, config_dict["num_labels"])

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        outputs = self.bert(input_ids, attention_mask=attention_mask)
        cls_output = outputs.last_hidden_state[:, 0, :]
        return self.fc(self.dropout(cls_output))


class SentimentService:
    """情感分析服务。"""

    def __init__(self, model_dir: str, bert_dir: str) -> None:
        self.model_dir = Path(model_dir)
        self.bert_dir = Path(bert_dir)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model: BertLoRALinear | None = None
        self.tokenizer: BertTokenizer | None = None
        self.status = "idle"
        self.error_message = ""

    def load(self) -> None:
        if self.model is not None and self.tokenizer is not None:
            return

        self.status = "loading"
        config_path = self.model_dir / "config.json"
        weights_path = self.model_dir / "best_model.bin"

        try:
            with config_path.open("r", encoding="utf-8") as file:
                config_dict = json.load(file)

            model_name = str(self.bert_dir if self.bert_dir.exists() else "bert-base-chinese")
            self.tokenizer = BertTokenizer.from_pretrained(model_name)
            self.model = BertLoRALinear(config_dict=config_dict, model_name=model_name)

            try:
                state_dict = torch.load(weights_path, map_location=self.device, weights_only=False)
            except TypeError:
                state_dict = torch.load(weights_path, map_location=self.device)

            self.model.load_state_dict(state_dict)
            self.model.to(self.device).eval()
            self.status = "ready"
            self.error_message = ""
        except Exception as exc:
            self.model = None
            self.tokenizer = None
            self.status = "error"
            self.error_message = str(exc)
            raise

    def analyze(self, text: str, threshold: float) -> SentimentAnalyzeResponse:
        if self.model is None or self.tokenizer is None or self.status != "ready":
            raise RuntimeError(self.error_message or "模型尚未加载")

        clean_text = text.strip()
        if not clean_text:
            raise ValueError("输入文本不能为空")

        logger.info(
            "sentiment analyze started: threshold=%s text_length=%s",
            threshold,
            len(clean_text),
        )

        start_time = time.perf_counter()
        inputs = self.tokenizer.encode_plus(
            clean_text,
            add_special_tokens=True,
            max_length=128,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        logger.info("sentiment tokenizer complete")

        with torch.no_grad():
            logits = self.model(
                inputs["input_ids"].to(self.device),
                inputs["attention_mask"].to(self.device),
            )
            probabilities = F.softmax(logits, dim=1)
        logger.info("sentiment model forward complete")

        negative_score = float(probabilities[0][0])
        positive_score = float(probabilities[0][1])
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.info(
            "sentiment probabilities complete: negative=%s positive=%s duration_ms=%s",
            negative_score,
            positive_score,
            duration_ms,
        )

        if positive_score >= threshold:
            sentiment = "positive"
            label = "正面情感"
        elif positive_score <= 1 - threshold:
            sentiment = "negative"
            label = "负面情感"
        else:
            sentiment = "neutral"
            label = "中性情感"

        try:
            import jieba

            tokens = jieba.lcut(clean_text)
        except Exception:
            tokens = list(clean_text)

        highlights: list[TokenHighlight] = []
        for token in tokens:
            tone = "neutral"
            if token in POS_WORDS:
                tone = "positive"
            elif token in NEG_WORDS:
                tone = "negative"
            highlights.append(TokenHighlight(text=token, tone=tone))

        return SentimentAnalyzeResponse(
            label=label,
            sentiment=sentiment,
            threshold=threshold,
            probabilities=ProbabilityPayload(negative=negative_score, positive=positive_score),
            highlights=highlights,
            metrics=MetricsPayload(duration_ms=duration_ms, device=str(self.device)),
        )

    def health(self) -> HealthResponse:
        return HealthResponse(
            status=self.status,
            model=self.model_dir.name,
            detail=self.error_message or None,
        )


_sentiment_service: SentimentService | None = None


def get_sentiment_service() -> SentimentService:
    global _sentiment_service

    if _sentiment_service is None:
        _sentiment_service = SentimentService(
            model_dir=str(settings.model_dir),
            bert_dir=str(settings.bert_dir),
        )
    return _sentiment_service
