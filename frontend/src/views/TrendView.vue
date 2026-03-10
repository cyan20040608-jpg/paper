<template>
  <div class="trend-view">
    <section class="history-panel">
      <div class="history-panel__header">
        <div>
          <h3>情绪趋势图</h3>
          <p>根据情感分析页面产生的历史记录绘制</p>
        </div>
      </div>

      <DashboardChartPanel
        v-if="chartOption"
        title="正负面情绪变化"
        subtitle="按提交时间展示正面率与负面率"
        :option="chartOption"
      />

      <div v-else class="empty-state">
        <p>暂无历史记录</p>
        <span>请先在“情感分析”页面提交评论内容。</span>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import DashboardChartPanel from "../components/DashboardChartPanel.vue";
import { loadHistoryRecords } from "../utils/history";

const records = ref([]);

const chartOption = computed(() => {
  if (!records.value.length) {
    return null;
  }

  const sortedRecords = [...records.value].reverse();

  return {
    color: ["#22c55e", "#ef4444"],
    tooltip: {
      trigger: "axis"
    },
    legend: {
      bottom: 0,
      data: ["正面率", "负面率"]
    },
    grid: {
      left: 40,
      right: 24,
      top: 36,
      bottom: 48
    },
    xAxis: {
      type: "category",
      data: sortedRecords.map((item) => item.submitTime),
      axisLabel: {
        color: "#64748b",
        rotate: 20
      },
      axisLine: {
        lineStyle: {
          color: "#d9e2ef"
        }
      }
    },
    yAxis: {
      type: "value",
      min: 0,
      max: 100,
      axisLabel: {
        color: "#94a3b8",
        formatter: "{value}%"
      },
      splitLine: {
        lineStyle: {
          color: "#eef2f8"
        }
      }
    },
    series: [
      {
        name: "正面率",
        type: "line",
        smooth: true,
        data: sortedRecords.map((item) => item.positiveRate),
        symbolSize: 8,
        lineStyle: {
          width: 3
        }
      },
      {
        name: "负面率",
        type: "line",
        smooth: true,
        data: sortedRecords.map((item) => item.negativeRate),
        symbolSize: 8,
        lineStyle: {
          width: 3
        }
      }
    ]
  };
});

onMounted(() => {
  records.value = loadHistoryRecords();
});
</script>
