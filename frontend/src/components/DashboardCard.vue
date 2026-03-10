<template>
  <section class="dashboard-card">
    <div class="dashboard-card__icon" :style="{ background: iconColor }">{{ iconText }}</div>
    <p class="dashboard-card__label">{{ label }}</p>
    <p class="dashboard-card__value">{{ value }}</p>
    <p class="dashboard-card__hint">{{ hint }}</p>
  </section>
</template>

<script setup>
defineProps({
  label: {
    type: String,
    required: true
  },
  value: {
    type: String,
    required: true
  },
  hint: {
    type: String,
    default: ""
  },
  iconText: {
    type: String,
    default: "数"
  },
  iconColor: {
    type: String,
    default: "#dbeafe"
  }
});
</script>
