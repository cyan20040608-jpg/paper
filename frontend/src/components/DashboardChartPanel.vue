<template>
  <section class="chart-panel">
    <div class="chart-panel__header">
      <div>
        <h3>{{ title }}</h3>
        <p>{{ subtitle }}</p>
      </div>
    </div>
    <div ref="chartRef" class="chart-panel__canvas"></div>
  </section>
</template>

<script setup>
import * as echarts from "echarts";
import { onBeforeUnmount, onMounted, ref, watch } from "vue";

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ""
  },
  option: {
    type: Object,
    required: true
  }
});

const chartRef = ref(null);
let chartInstance = null;

function renderChart() {
  if (!chartRef.value) {
    return;
  }

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value);
  }

  chartInstance.setOption(props.option, true);
}

function handleResize() {
  if (chartInstance) {
    chartInstance.resize();
  }
}

watch(
  () => props.option,
  () => {
    renderChart();
  },
  { deep: true }
);

onMounted(() => {
  renderChart();
  window.addEventListener("resize", handleResize);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", handleResize);
  if (chartInstance) {
    chartInstance.dispose();
    chartInstance = null;
  }
});
</script>
