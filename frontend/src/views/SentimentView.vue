<template>
  <div class="sentiment-view">
    <section class="sentiment-stage">
      <section class="sentiment-form card-shell">
        <div class="sentiment-form__header">
          <div>
            <p class="sentiment-form__eyebrow">输入面板</p>
            <h3>文本情感分析</h3>
          </div>
          <div class="sentiment-form__health" :class="`is-${healthTag}`">{{ healthText }}</div>
        </div>

        <label class="field-block">
          <span>输入文本</span>
          <textarea
            v-model="form.text"
            rows="7"
            placeholder="请输入校园论坛帖子、评论或任意中文文本"
          ></textarea>
        </label>

        <label class="field-block">
          <span>判定阈值 {{ form.threshold.toFixed(2) }}</span>
          <input v-model.number="form.threshold" type="range" min="0.5" max="0.95" step="0.01" />
        </label>

        <div class="threshold-scale">
          <span>0.50</span>
          <span>更保守</span>
          <span>0.95</span>
        </div>

        <div class="sentiment-form__actions">
          <button class="primary-button" type="button" :disabled="isAnalyzeDisabled" @click="handleAnalyze">
            {{ analyzeButtonText }}
          </button>
          <button class="secondary-button" type="button" :disabled="loading" @click="handleReset">
            重置
          </button>
        </div>

        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

        <div class="sentiment-form__tips">
          <span>推荐输入：评价、帖子、评论、短句</span>
          <span>输出包含标签、概率、高亮与原始数据</span>
        </div>
      </section>
    </section>

    <div class="sentiment-results">
      <div class="result-banner card-shell" :class="{ 'is-empty': !result }">
        <span class="result-banner__dot" :class="result ? `is-${result.sentiment}` : 'is-idle'"></span>
        <strong>{{ result ? result.label : "等待模型输出" }}</strong>
      </div>

      <SentimentResultPanel :result="result" />
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from "vue";
import { analyzeSentiment, fetchHealth } from "../api/sentiment";
import SentimentResultPanel from "../components/SentimentResultPanel.vue";
import { appendHistoryRecord } from "../utils/history";

const defaultText = "这家店味道真的绝了，服务也很周到，下次还来。";
const healthPollIntervalMs = 3000;

const form = reactive({
  text: defaultText,
  threshold: 0.6
});

const loading = ref(false);
const result = ref(null);
const errorMessage = ref("");
const healthStatus = ref("idle");
const healthDetail = ref("");
const healthRequesting = ref(false);

let healthTimer = null;

const healthTag = computed(() => {
  if (healthStatus.value === "ready") {
    return "ready";
  }

  if (healthStatus.value === "error" || healthStatus.value === "unreachable") {
    return "error";
  }

  return "idle";
});

const healthText = computed(() => {
  if (healthStatus.value === "ready") {
    return "模型已就绪";
  }

  if (healthStatus.value === "loading") {
    return "模型加载中";
  }

  if (healthStatus.value === "error") {
    return healthDetail.value || "模型异常";
  }

  if (healthStatus.value === "unreachable") {
    return "连接后端失败";
  }

  return "正在检测";
});

const isAnalyzeDisabled = computed(() => {
  return loading.value || healthStatus.value !== "ready";
});

const analyzeButtonText = computed(() => {
  if (loading.value) {
    return "分析中...";
  }

  if (healthStatus.value === "loading") {
    return "模型加载中";
  }

  return "开始分析";
});

async function loadHealth() {
  if (healthRequesting.value) {
    return;
  }

  healthRequesting.value = true;

  try {
    const response = await fetchHealth();
    const backendStatus = response.data.status || "idle";

    healthStatus.value = backendStatus;
    healthDetail.value = response.data.detail || "";

    if (backendStatus === "ready") {
      errorMessage.value = "";
    }
  } catch (error) {
    healthStatus.value = "unreachable";
    healthDetail.value = error?.message || "";
  } finally {
    healthRequesting.value = false;
  }
}

async function handleAnalyze() {
  if (isAnalyzeDisabled.value) {
    if (healthStatus.value === "loading") {
      errorMessage.value = "模型加载中，请稍后再试。";
      await loadHealth();
    }
    return;
  }

  loading.value = true;
  errorMessage.value = "";

  try {
    const response = await analyzeSentiment({
      text: form.text,
      threshold: Number(form.threshold)
    });

    result.value = response.data;
    healthStatus.value = "ready";
    healthDetail.value = "";

    appendHistoryRecord({
      id: `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`,
      comment: form.text.trim(),
      positiveRate: Number((response.data.probabilities.positive * 100).toFixed(2)),
      negativeRate: Number((response.data.probabilities.negative * 100).toFixed(2)),
      submitTime: new Date().toLocaleString("zh-CN", { hour12: false }),
      highlights: response.data.highlights || []
    });
  } catch (error) {
    result.value = null;

    if (error?.response?.status === 503) {
      errorMessage.value = error?.response?.data?.detail || "模型加载中，请稍后再试。";
      await loadHealth();
    } else {
      errorMessage.value =
        error?.response?.data?.detail || "分析请求失败，请检查后端服务是否已经启动。";
    }
  } finally {
    loading.value = false;
  }
}

function handleReset() {
  form.text = defaultText;
  form.threshold = 0.6;
  result.value = null;
  errorMessage.value = "";
}

function startHealthPolling() {
  if (healthTimer !== null) {
    return;
  }

  healthTimer = window.setInterval(() => {
    if (healthStatus.value !== "ready") {
      void loadHealth();
    }
  }, healthPollIntervalMs);
}

function stopHealthPolling() {
  if (healthTimer !== null) {
    window.clearInterval(healthTimer);
    healthTimer = null;
  }
}

onMounted(async () => {
  await loadHealth();
  startHealthPolling();
});

onBeforeUnmount(() => {
  stopHealthPolling();
});
</script>
