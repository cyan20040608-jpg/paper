<template>
  <section class="result-panel">
    <div class="result-panel__header">
      <div>
        <p class="result-panel__eyebrow">判定结果</p>
        <h3>{{ result ? result.label : "等待分析" }}</h3>
      </div>
      <div v-if="result" class="result-panel__badge" :class="`is-${result.sentiment}`">
        {{ toneMap[result.sentiment] }}
      </div>
    </div>

    <template v-if="result">
      <div class="result-summary">
        <div class="result-summary__card is-strong">
          <span>正面置信度</span>
          <strong>{{ formatPercent(result.probabilities.positive) }}</strong>
        </div>
        <div class="result-summary__card">
          <span>负面概率</span>
          <strong>{{ formatPercent(result.probabilities.negative) }}</strong>
        </div>
        <div class="result-summary__card">
          <span>判定阈值</span>
          <strong>{{ result.threshold.toFixed(2) }}</strong>
        </div>
      </div>

      <div class="result-panel__metrics">
        <span>阈值 {{ result.threshold.toFixed(2) }}</span>
        <span>耗时 {{ result.metrics.duration_ms }} ms</span>
        <span>设备 {{ result.metrics.device }}</span>
      </div>

      <div class="probability-list">
        <div class="probability-item">
          <div class="probability-item__label">
            <span>正面概率</span>
            <strong>{{ formatPercent(result.probabilities.positive) }}</strong>
          </div>
          <div class="probability-item__bar">
            <span
              class="probability-item__fill is-positive"
              :style="{ width: `${result.probabilities.positive * 100}%` }"
            ></span>
          </div>
        </div>

        <div class="probability-item">
          <div class="probability-item__label">
            <span>负面概率</span>
            <strong>{{ formatPercent(result.probabilities.negative) }}</strong>
          </div>
          <div class="probability-item__bar">
            <span
              class="probability-item__fill is-negative"
              :style="{ width: `${result.probabilities.negative * 100}%` }"
            ></span>
          </div>
        </div>
      </div>

      <div class="highlight-box">
        <p class="highlight-box__title">关键词高亮</p>
        <div class="highlight-box__content">
          <span
            v-for="(item, index) in result.highlights"
            :key="`${item.text}-${index}`"
            class="highlight-token"
            :class="`is-${item.tone}`"
          >
            {{ item.text }}
          </span>
        </div>
      </div>

      <div class="raw-data-box">
        <p class="highlight-box__title">原始数据</p>
        <pre>{{ formatJson(result) }}</pre>
      </div>
    </template>

    <p v-else class="result-panel__empty">
      输入文本并点击“开始分析”后，这里会显示模型判断结果。
    </p>
  </section>
</template>

<script setup>
defineProps({
  result: {
    type: Object,
    default: null
  }
});

const toneMap = {
  positive: "正向",
  negative: "负向",
  neutral: "中性"
};

function formatPercent(value) {
  return `${(value * 100).toFixed(1)}%`;
}

function formatJson(value) {
  return JSON.stringify(value, null, 2);
}
</script>
