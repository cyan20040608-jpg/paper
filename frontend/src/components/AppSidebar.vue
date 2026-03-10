<template>
  <aside class="sidebar">
    <div class="sidebar-brand">
      <div class="sidebar-brand__logo">N</div>
      <div>
        <h1 class="sidebar-brand__title">NLP 情感分析系统</h1>
        <p class="sidebar-brand__subtitle">BERT + LoRA</p>
      </div>
    </div>

    <nav class="sidebar-nav">
      <div v-for="section in menuSections" :key="section.title" class="sidebar-section">
        <p class="sidebar-section__title">{{ section.title }}</p>
        <button
          v-for="item in section.items"
          :key="item.label"
          class="sidebar-item"
          :class="{ 'is-active': item.routeName === route.name }"
          type="button"
          @click="handleNavigate(item.routeName)"
        >
          <span class="sidebar-item__icon">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </button>
      </div>
    </nav>
  </aside>
</template>

<script setup>
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();

const menuSections = [
  {
    title: "功能菜单",
    items: [
      { label: "情感分析", routeName: "sentiment", icon: "析" },
      { label: "情绪趋势图", routeName: "trend", icon: "势" },
      { label: "高频词统计", routeName: "wordStats", icon: "词" },
      { label: "历史记录", routeName: "history", icon: "记" }
    ]
  }
];

function handleNavigate(routeName) {
  router.push({ name: routeName });
}
</script>
