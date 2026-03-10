<template>
  <div class="word-stats-view">
    <section class="dashboard-grid">
      <DashboardCard label="评论条数" :value="String(records.length)" hint="已分析评论数" icon-text="评" icon-color="#dfe7ff" />
      <DashboardCard label="有效词数" :value="String(uniqueWordCount)" hint="去重后的统计词汇" icon-text="词" icon-color="#dcfce7" />
      <DashboardCard label="最高频词" :value="topWordLabel" hint="出现次数最多的词" icon-text="高" icon-color="#fef3c7" />
      <DashboardCard label="最高频次数" :value="String(topWordCount)" hint="统计范围为历史记录" icon-text="次" icon-color="#fee2e2" />
    </section>

    <section v-if="chartOption" class="dashboard-charts">
      <DashboardChartPanel title="高频词统计" subtitle="基于历史评论文本的词频统计" :option="chartOption" />
      <section class="history-panel">
        <div class="history-panel__header">
          <div>
            <h3>高频词列表</h3>
            <p>展示出现次数最高的词</p>
          </div>
        </div>
        <div class="word-tag-list">
          <span v-for="item in topWords" :key="item.word" class="word-tag">
            {{ item.word }} {{ item.count }}
          </span>
        </div>
      </section>
    </section>

    <div v-else class="empty-state history-panel">
      <p>暂无高频词数据</p>
      <span>请先在“情感分析”页面提交评论内容。</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import DashboardCard from "../components/DashboardCard.vue";
import DashboardChartPanel from "../components/DashboardChartPanel.vue";
import { loadHistoryRecords } from "../utils/history";

const records = loadHistoryRecords();

function normalizeToken(token) {
  return String(token || "").replace(/[^\u4e00-\u9fa5A-Za-z0-9]/g, "").trim();
}

const topWords = computed(() => {
  const wordMap = new Map();

  records.forEach((record) => {
    const highlights = Array.isArray(record.highlights) ? record.highlights : [];
    highlights.forEach((item) => {
      const word = normalizeToken(item.text);
      if (!word) {
        return;
      }
      if (word.length < 2 && item.tone === "neutral") {
        return;
      }
      wordMap.set(word, (wordMap.get(word) || 0) + 1);
    });
  });

  return [...wordMap.entries()]
    .map(([word, count]) => ({ word, count }))
    .sort((left, right) => right.count - left.count)
    .slice(0, 10);
});

const uniqueWordCount = computed(() => topWords.value.length);
const topWordLabel = computed(() => topWords.value[0]?.word || "-");
const topWordCount = computed(() => topWords.value[0]?.count || 0);

const chartOption = computed(() => {
  if (!topWords.value.length) {
    return null;
  }

  return {
    color: ["#5b6cff"],
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "shadow"
      }
    },
    grid: {
      left: 80,
      right: 24,
      top: 30,
      bottom: 24
    },
    xAxis: {
      type: "value",
      axisLabel: {
        color: "#94a3b8"
      },
      splitLine: {
        lineStyle: {
          color: "#eef2f8"
        }
      }
    },
    yAxis: {
      type: "category",
      data: topWords.value.map((item) => item.word),
      axisLabel: {
        color: "#475569"
      },
      axisLine: {
        lineStyle: {
          color: "#d9e2ef"
        }
      }
    },
    series: [
      {
        type: "bar",
        data: topWords.value.map((item) => item.count),
        barWidth: 22,
        itemStyle: {
          borderRadius: [0, 10, 10, 0]
        },
        label: {
          show: true,
          position: "right",
          color: "#475569"
        }
      }
    ]
  };
});
</script>
