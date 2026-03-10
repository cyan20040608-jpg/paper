<template>
  <header class="page-header page-header--centered">
    <div class="page-header__info">
      <h2 class="page-header__title">{{ title }}</h2>
    </div>
  </header>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();

const title = computed(() => route.meta.title || "情感分析");
</script>
