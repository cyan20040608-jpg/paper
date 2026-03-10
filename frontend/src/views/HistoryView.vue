<template>
  <div class="history-page">
    <el-card class="history-card" shadow="never">
      <div class="history-toolbar">
        <div class="history-toolbar__left">
          <h3 class="history-toolbar__title">历史记录</h3>
          <p class="history-toolbar__subtitle">展示用户评论与情感分析结果</p>
        </div>

        <div class="history-toolbar__right">
          <el-input
            v-model="keyword"
            placeholder="搜索评论内容"
            clearable
            class="history-toolbar__search"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>

          <el-button
            type="danger"
            plain
            :disabled="filteredRecords.length === 0"
            @click="handleClearAll"
          >
            删除所有历史记录
          </el-button>
        </div>
      </div>

      <div class="history-overview">
        <div class="history-overview__card">
          <span class="history-overview__label">记录总数</span>
          <strong class="history-overview__value">{{ filteredRecords.length }}</strong>
        </div>
        <div class="history-overview__card">
          <span class="history-overview__label">正面记录</span>
          <strong class="history-overview__value is-positive">{{ positiveCount }}</strong>
        </div>
        <div class="history-overview__card">
          <span class="history-overview__label">负面记录</span>
          <strong class="history-overview__value is-negative">{{ negativeCount }}</strong>
        </div>
      </div>

      <el-table
        :data="filteredRecords"
        border
        stripe
        class="history-table"
        empty-text="暂无历史记录"
      >
        <el-table-column label="评论内容" min-width="320">
          <template #default="{ row }">
            <div class="comment-cell">
              <div class="comment-cell__text">{{ row.comment }}</div>
              <div class="comment-cell__meta">提交时间：{{ row.submitTime }}</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="情感结果" width="110" align="center">
          <template #default="{ row }">
            <el-tag
              round
              effect="light"
              :type="row.positiveRate >= row.negativeRate ? 'success' : 'danger'"
            >
              {{ row.positiveRate >= row.negativeRate ? "正面" : "负面" }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="正面率" min-width="180">
          <template #default="{ row }">
            <div class="progress-cell">
              <span class="progress-cell__value is-positive">{{ row.positiveRate }}%</span>
              <el-progress
                :percentage="row.positiveRate"
                :show-text="false"
                :stroke-width="8"
                color="#67c23a"
              />
            </div>
          </template>
        </el-table-column>

        <el-table-column label="负面率" min-width="180">
          <template #default="{ row }">
            <div class="progress-cell">
              <span class="progress-cell__value is-negative">{{ row.negativeRate }}%</span>
              <el-progress
                :percentage="row.negativeRate"
                :show-text="false"
                :stroke-width="8"
                color="#f56c6c"
              />
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="submitTime" label="提交评论时间" width="180" />

        <el-table-column label="操作" width="100" align="center" fixed="right">
          <template #default="{ row }">
            <el-popconfirm
              title="确认删除该条记录？"
              confirm-button-text="删除"
              cancel-button-text="取消"
              @confirm="handleDeleteOne(row.id)"
            >
              <template #reference>
                <el-button type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Search } from "@element-plus/icons-vue";
import { clearHistoryRecords, loadHistoryRecords, removeHistoryRecord } from "../utils/history";

const keyword = ref("");
const records = ref(loadHistoryRecords());

const filteredRecords = computed(() => {
  const text = keyword.value.trim();
  if (!text) {
    return records.value;
  }
  return records.value.filter((item) => item.comment.includes(text));
});

const positiveCount = computed(
  () => filteredRecords.value.filter((item) => item.positiveRate >= item.negativeRate).length
);

const negativeCount = computed(
  () => filteredRecords.value.filter((item) => item.positiveRate < item.negativeRate).length
);

function handleDeleteOne(recordId) {
  records.value = removeHistoryRecord(recordId);
  ElMessage.success("删除成功");
}

async function handleClearAll() {
  try {
    await ElMessageBox.confirm("确认删除所有历史记录？", "提示", {
      type: "warning",
      confirmButtonText: "删除",
      cancelButtonText: "取消"
    });
    records.value = clearHistoryRecords();
    ElMessage.success("已清空历史记录");
  } catch (error) {
    return;
  }
}
</script>

<style scoped>
.history-page {
  padding: 0;
}

.history-card {
  border: none;
  border-radius: 20px;
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.06);
}

.history-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 20px;
}

.history-toolbar__title {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #1f2d3d;
}

.history-toolbar__subtitle {
  margin: 6px 0 0;
  font-size: 13px;
  color: #909399;
}

.history-toolbar__right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.history-toolbar__search {
  width: 240px;
}

.history-overview {
  display: grid;
  grid-template-columns: repeat(3, 160px);
  gap: 12px;
  margin-bottom: 20px;
}

.history-overview__card {
  padding: 14px 16px;
  border-radius: 14px;
  background: #f8fafc;
}

.history-overview__label {
  font-size: 12px;
  color: #909399;
}

.history-overview__value {
  display: block;
  margin-top: 8px;
  font-size: 22px;
  font-weight: 700;
  color: #303133;
}

.history-overview__value.is-positive {
  color: #67c23a;
}

.history-overview__value.is-negative {
  color: #f56c6c;
}

.history-table :deep(.el-table__cell) {
  padding: 10px 0;
}

.comment-cell {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.comment-cell__text {
  line-height: 1.6;
  color: #303133;
}

.comment-cell__meta {
  font-size: 12px;
  color: #a8abb2;
}

.progress-cell {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-cell__value {
  font-size: 13px;
  font-weight: 600;
}

.progress-cell__value.is-positive {
  color: #67c23a;
}

.progress-cell__value.is-negative {
  color: #f56c6c;
}

@media (max-width: 900px) {
  .history-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .history-toolbar__right {
    flex-direction: column;
    align-items: stretch;
  }

  .history-toolbar__search {
    width: 100%;
  }

  .history-overview {
    grid-template-columns: 1fr;
  }
}
</style>
