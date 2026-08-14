<template>
  <div class="dashboard">
    <!-- Welcome section -->
    <section class="welcome-section">
      <div class="welcome-text">
        <h1 class="welcome-title">
          欢迎回来{{ authStore.user?.email ? `，${authStore.user.email.split('@')[0]}` : '' }}
        </h1>
        <p class="welcome-desc">
          你有 <strong>{{ knowledgeStore.kbCount }}</strong> 个知识库
          <template v-if="knowledgeStore.kbCount > 0">
            ，最近创建于 {{ lastActive }}
          </template>
        </p>
      </div>
      <div class="welcome-badge">
        <el-tag :type="authStore.isAdmin ? 'danger' : 'primary'" size="default" class="role-badge">
          {{ authStore.isAdmin ? '管理员' : '普通用户' }}
        </el-tag>
      </div>
    </section>

    <!-- Stats row -->
    <section class="stats-row">
      <div class="stat-card">
        <div class="stat-value">{{ knowledgeStore.kbCount }}</div>
        <div class="stat-label">知识库</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ totalDocuments }}</div>
        <div class="stat-label">文档</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ totalOrganizations }}</div>
        <div class="stat-label">组织</div>
      </div>
    </section>

    <!-- Knowledge base grid -->
    <section class="kb-section">
      <div class="section-header">
        <h2 class="section-title">我的知识库</h2>
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">
          新建知识库
        </el-button>
      </div>
      <KnowledgeBaseGrid
        :knowledge-bases="knowledgeStore.knowledgeBases"
        :loading="knowledgeStore.loading"
        :error="knowledgeStore.error"
        @select="goToKnowledgeBase"
        @chat="goToKnowledgeBase"
        @browse="goToDocuments"
        @edit="openEditDialog"
        @delete="handleDelete"
        @retry="knowledgeStore.loadKnowledgeBases()"
      />
    </section>

    <!-- Admin quick access -->
    <section v-if="authStore.isAdmin" class="admin-section">
      <div class="section-header">
        <h2 class="section-title">管理功能</h2>
      </div>
      <el-card shadow="never" class="admin-card">
        <div class="admin-card-content">
          <div class="admin-info">
            <el-icon :size="28" color="var(--color-primary)"><List /></el-icon>
            <div>
              <p class="admin-title">注册申请管理</p>
              <p class="admin-desc">审核和处理用户注册申请</p>
            </div>
          </div>
          <el-button type="primary" @click="$router.push('/admin/requests')">
            前往管理
          </el-button>
        </div>
      </el-card>
    </section>

    <!-- Create / Edit dialog -->
    <KnowledgeBaseFormDialog
      v-model="dialogVisible"
      :kb="editingKb"
      :organizations="organizations"
      :is-admin="authStore.isAdmin"
      :submitting="submitting"
      @submit="handleFormSubmit"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { List, Plus } from '@element-plus/icons-vue'
import type { KnowledgeBaseSimple } from '@/types/knowledge'
import { useAuthStore } from '@/stores/auth'
import { useKnowledgeStore } from '@/stores/knowledge'
import KnowledgeBaseGrid from '@/components/knowledge/KnowledgeBaseGrid.vue'
import KnowledgeBaseFormDialog from '@/components/knowledge/KnowledgeBaseFormDialog.vue'
import { fetchOrganizations } from '@/api/organization'
import type { OrganizationOut } from '@/types/knowledge'

const router = useRouter()
const authStore = useAuthStore()
const knowledgeStore = useKnowledgeStore()

const organizations = ref<OrganizationOut[]>([])
const dialogVisible = ref(false)
const editingKb = ref<KnowledgeBaseSimple | null>(null)
const submitting = ref(false)

const totalDocuments = computed(() =>
  knowledgeStore.knowledgeBases.reduce((sum, kb) => sum + kb.document_count, 0)
)

const totalOrganizations = computed(() => organizations.value.length)

const lastActive = computed(() => {
  if (knowledgeStore.knowledgeBases.length === 0) return ''
  const dates = knowledgeStore.knowledgeBases.map((kb) => new Date(kb.created_at).getTime())
  const latest = new Date(Math.max(...dates))
  return latest.toLocaleDateString('zh-CN')
})

function goToKnowledgeBase(id: number) {
  router.push(`/knowledge/${id}`)
}

function goToDocuments(id: number) {
  router.push(`/knowledge/${id}/documents`)
}

function openCreateDialog() {
  editingKb.value = null
  dialogVisible.value = true
}

function openEditDialog(id: number) {
  const kb = knowledgeStore.getKnowledgeBase(id)
  if (!kb) return
  editingKb.value = kb
  dialogVisible.value = true
}

async function handleDelete(id: number) {
  const kb = knowledgeStore.getKnowledgeBase(id)
  try {
    await ElMessageBox.confirm(
      `确定删除知识库「${kb?.name || id}」吗？删除后不可恢复。`,
      '删除确认',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }
    )
  } catch {
    return // 用户取消
  }
  try {
    await knowledgeStore.remove(id)
    ElMessage.success('知识库已删除')
  } catch {
    // http 拦截器已提示错误信息
  }
}

async function handleFormSubmit(payload: { id?: number; data: any }) {
  submitting.value = true
  try {
    if (payload.id !== undefined) {
      await knowledgeStore.update(payload.id, payload.data)
      ElMessage.success('知识库已更新')
    } else {
      await knowledgeStore.create(payload.data)
      ElMessage.success('知识库创建成功')
    }
    dialogVisible.value = false
  } catch {
    // http 拦截器已提示错误信息
  } finally {
    submitting.value = false
  }
}

async function loadOrganizations() {
  try {
    organizations.value = await fetchOrganizations()
  } catch {
    organizations.value = []
  }
}

onMounted(() => {
  knowledgeStore.loadKnowledgeBases()
  loadOrganizations()
})
</script>

<style scoped>
.dashboard {
  max-width: var(--content-max-width);
  margin: 0 auto;
}

/* Welcome section */
.welcome-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-8);
}

.welcome-title {
  font-family: var(--font-heading);
  font-size: var(--text-3xl);
  font-weight: 700;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: var(--space-2);
}

.welcome-desc {
  font-size: var(--text-base);
  color: var(--color-muted-foreground);
}

.welcome-desc strong {
  color: var(--color-primary);
  font-weight: 600;
}

.role-badge {
  font-weight: 500;
}

/* Stats row */
.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-5);
  margin-bottom: var(--space-8);
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
  border-color: var(--color-border);
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

/* Section headers */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-5);
}

.section-title {
  font-family: var(--font-heading);
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--color-foreground);
}

.kb-section {
  margin-bottom: var(--space-8);
}

/* Admin section */
.admin-card {
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border-light);
}

.admin-card-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-5);
}

.admin-info {
  display: flex;
  align-items: center;
  gap: var(--space-5);
}

.admin-title {
  font-weight: 600;
  color: var(--color-foreground);
  margin-bottom: 2px;
}

.admin-desc {
  font-size: var(--text-sm);
  color: var(--color-muted-foreground);
}

@media (max-width: 640px) {
  .stats-row {
    grid-template-columns: 1fr;
  }
}
</style>
