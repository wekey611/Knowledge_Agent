<template>
  <div class="admin-requests">
    <!-- Stats row -->
    <section class="stats-row">
      <div class="stat-card total">
        <div class="stat-value">{{ stats.total }}</div>
        <div class="stat-label">全部申请</div>
      </div>
      <div class="stat-card pending-stat">
        <div class="stat-value">{{ stats.pending }}</div>
        <div class="stat-label">待审批</div>
      </div>
      <div class="stat-card approved-stat">
        <div class="stat-value">{{ stats.approved }}</div>
        <div class="stat-label">已通过</div>
      </div>
    </section>

    <!-- Filter tabs -->
    <section class="filter-section">
      <div class="filter-tabs">
        <button
          v-for="tab in filterTabs"
          :key="tab.key"
          class="filter-tab"
          :class="{ active: activeFilter === tab.key }"
          @click="activeFilter = tab.key"
        >
          {{ tab.label }}
          <span class="filter-count">{{ tab.count }}</span>
        </button>
      </div>
      <el-button size="small" :icon="Refresh" @click="fetchData">
        刷新
      </el-button>
    </section>

    <!-- Loading state -->
    <EmptyState
      v-if="loading"
      type="loading"
      title="加载中..."
      description="正在加载注册申请列表"
    />

    <!-- Error state -->
    <EmptyState
      v-else-if="error"
      type="error"
      title="加载失败"
      :description="error"
      action-label="重试"
      @action="fetchData"
    />

    <!-- Empty state -->
    <EmptyState
      v-else-if="filteredRequests.length === 0"
      type="empty"
      title="暂无申请"
      description="当前没有符合条件的注册申请"
    />

    <!-- Table -->
    <el-card v-else shadow="never" class="table-card">
      <el-table
        :data="filteredRequests"
        v-loading="loading"
        style="width: 100%"
        stripe
        :header-cell-style="{ background: 'var(--color-muted)', color: 'var(--color-foreground)' }"
      >
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="email" label="邮箱" min-width="200">
          <template #default="{ row }">
            <span class="cell-email">{{ row.email }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="申请理由" min-width="250" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small" class="status-tag">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right" align="center">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              :disabled="row.status !== 'pending'"
              :loading="approvingId === row.id"
              class="action-btn"
              @click="handleApprove(row.id)"
            >
              {{ approvingId === row.id ? '审批中' : '审批通过' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import type { UserRequestOutput } from '@/types/api'
import { getRequests, approveRequest } from '@/api/admin'
import EmptyState from '@/components/common/EmptyState.vue'

const loading = ref(false)
const error = ref<string | null>(null)
const approvingId = ref<number | null>(null)
const requests = ref<UserRequestOutput[]>([])
const activeFilter = ref<string>('all')

const stats = computed(() => {
  const total = requests.value.length
  const pending = requests.value.filter((r) => r.status === 'pending').length
  const approved = requests.value.filter((r) => r.status === 'approved' || r.status === 'registered').length
  return { total, pending, approved }
})

const filterTabs = computed(() => [
  { key: 'all', label: '全部', count: stats.value.total },
  { key: 'pending', label: '待审批', count: stats.value.pending },
  { key: 'approved', label: '已通过', count: stats.value.approved },
])

const filteredRequests = computed(() => {
  if (activeFilter.value === 'all') return requests.value
  return requests.value.filter((r) => {
    if (activeFilter.value === 'pending') return r.status === 'pending'
    if (activeFilter.value === 'approved') return r.status === 'approved' || r.status === 'registered'
    return true
  })
})

function statusType(status: string | null): string {
  const map: Record<string, string> = {
    pending: 'warning',
    approved: 'success',
    registered: 'info',
    expired: 'danger',
  }
  return map[status || ''] || 'info'
}

function statusLabel(status: string | null): string {
  const map: Record<string, string> = {
    pending: '待审批',
    approved: '已通过',
    registered: '已注册',
    expired: '已过期',
  }
  return map[status || ''] || status || '未知'
}

async function fetchData() {
  loading.value = true
  error.value = null
  try {
    requests.value = await getRequests()
  } catch (e: any) {
    error.value = e?.message || '加载申请列表失败'
  } finally {
    loading.value = false
  }
}

async function handleApprove(requestId: number) {
  try {
    await ElMessageBox.confirm('确认审批通过该注册申请？系统将发送邀请邮件。', '确认操作', {
      confirmButtonText: '确认通过',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'confirm-btn',
    })
  } catch {
    return
  }

  approvingId.value = requestId
  try {
    const res = await approveRequest(requestId)
    ElMessage.success(`已通过 ${res.email} 的申请，邀请邮件已发送`)
    const idx = requests.value.findIndex((r) => r.id === requestId)
    if (idx !== -1) {
      requests.value[idx].status = 'approved'
    }
  } catch {
    // Error handled by interceptor
  } finally {
    approvingId.value = null
  }
}

onMounted(fetchData)
</script>

<style scoped>
.admin-requests {
  max-width: var(--content-max-width);
  margin: 0 auto;
}

/* Stats */
.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-5);
  margin-bottom: var(--space-6);
}

.stat-card {
  background: var(--color-card);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  text-align: center;
  transition: all var(--transition-normal);
}

.stat-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.stat-card.total:hover {
  box-shadow: var(--shadow-md), var(--glow-primary);
  border-left-color: var(--color-cyan);
}

.stat-card.pending-stat {
  border-left: 4px solid var(--color-warning);
}

.stat-card.pending-stat:hover {
  box-shadow: var(--shadow-md), 0 0 20px rgba(245, 158, 11, 0.15);
}

.stat-card.approved-stat {
  border-left: 4px solid var(--color-success);
}

.stat-card.approved-stat:hover {
  box-shadow: var(--shadow-md), 0 0 20px rgba(16, 185, 129, 0.15);
}

.stat-card.total {
  border-left: 4px solid var(--color-primary);
}

.stat-value {
  font-family: var(--font-heading);
  font-size: var(--text-4xl);
  font-weight: 700;
  color: var(--color-foreground);
  line-height: 1.2;
  margin-bottom: var(--space-1);
}

.stat-label {
  font-size: var(--text-sm);
  color: var(--color-muted-foreground);
}

/* Filter tabs */
.filter-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-5);
}

.filter-tabs {
  display: flex;
  gap: var(--space-2);
}

.filter-tab {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-5);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-light);
  background: transparent;
  font-size: var(--text-sm);
  color: var(--color-muted-foreground);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.filter-tab:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.filter-tab.active {
  background: var(--color-primary-bg);
  border-color: var(--color-primary);
  color: var(--color-primary);
  font-weight: 500;
}

.filter-count {
  font-size: var(--text-xs);
  opacity: 0.7;
}

/* Table */
.table-card {
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border-light);
}

.cell-email {
  font-weight: 500;
}

.status-tag {
  font-weight: 500;
}

.action-btn {
  font-weight: 500;
}
</style>
