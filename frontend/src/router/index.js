import { createRouter, createWebHistory } from "vue-router";
import AdminLayout from "../layouts/AdminLayout.vue";
import HistoryView from "../views/HistoryView.vue";
import SentimentView from "../views/SentimentView.vue";
import TrendView from "../views/TrendView.vue";
import WordStatsView from "../views/WordStatsView.vue";

const routes = [
  {
    path: "/",
    component: AdminLayout,
    children: [
      {
        path: "",
        redirect: { name: "sentiment" }
      },
      {
        path: "sentiment",
        name: "sentiment",
        component: SentimentView,
        meta: {
          title: "情感分析"
        }
      },
      {
        path: "trend",
        name: "trend",
        component: TrendView,
        meta: {
          title: "情绪趋势图"
        }
      },
      {
        path: "word-stats",
        name: "wordStats",
        component: WordStatsView,
        meta: {
          title: "高频词统计"
        }
      },
      {
        path: "history",
        name: "history",
        component: HistoryView,
        meta: {
          title: "历史记录"
        }
      }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
