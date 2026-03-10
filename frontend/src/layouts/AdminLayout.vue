<template>
  <div class="admin-shell">
    <AppSidebar />
    <div class="admin-main">
      <AppHeader />
      <main class="admin-content">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup>
import { RouterView } from "vue-router";
import AppHeader from "../components/AppHeader.vue";
import AppSidebar from "../components/AppSidebar.vue";
</script>
