<template>
  <div class="org-page">
    <!-- Header -->
    <section class="org-header">
      <div class="org-header-text">
        <h1 class="org-title">我的组织</h1>
        <p class="org-desc">创建组织，与团队协作管理知识库</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="openCreate">
        创建组织
      </el-button>
    </section>

    <!-- Loading -->
    <div v-if="loading" class="org-grid">
      <el-skeleton v-for="i in 4" :key="i" animated class="org-skeleton" />
    </div>

    <!-- Empty -->
    <EmptyState
      v-else-if="organizations.length === 0"
      type="empty"
      title="暂无组织"
      description="创建你的第一个组织，邀请成员一起管理和探索知识"
      action-label="创建组织"
      @action="openCreate"
    />

    <!-- Org grid -->
    <div v-else class="org-grid">
      <div
        v-for="org in organizations"
        :key="org.id"
        class="org-card"
        @click="$router.push(`/organizations/${org.id}`)"
      >
        <div class="org-card-header">
          <div class="org-avatar">{{ org.name.charAt(0).toUpperCase() }}</div>
          <div class="org-name-group">
            <h3 class="org-name">{{ org.name }}</h3>
            <span class="org-owner">
              所有者：{{ org.owner?.username || org.owner?.email || '未知' }}
            </span>
          </div>
        </div>
        <p class="org-desc-text">{{ org.description || '暂无描述' }}</p>
        <div class="org-footer">
          <span class="org-meta">{{ org.members?.length || 0 }} 名成员</span>
          <span class="org-meta">创建于 {{ formatDate(org.created_at) }}</span>
        </div>
      </div>
    </div>

    <!-- Create dialog -->
    <el-dialog
      v-model="dialogVisible"
      title="创建组织"
      width="480px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input
            v-model="form.name"
            placeholder="组织名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="组织描述（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleCreate">
          创建
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { Organization } from '@/types/knowledge'
import { createOrganization, fetchOrganizations } from '@/api/organization'
import EmptyState from '@/components/common/EmptyState.vue'

const organizations = ref<Organization[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()

const form = ref({ name: '', description: '' })
const rules: FormRules = {
  name: [
    { required: true, message: '请输入组织名称', trigger: 'blur' },
    { max: 100, message: '名称不能超过 100 个字符', trigger: 'blur' },
  ],
}

function openCreate() {
  form.value = { name: '', description: '' }
  dialogVisible.value = true
}

async function handleCreate() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    await createOrganization({
      name: form.value.name.trim(),
      description: form.value.description.trim(),
    })
    ElMessage.success('组织创建成功')
    dialogVisible.value = false
    await load()
  } catch {
    // http 拦截器已提示
  } finally {
    submitting.value = false
  }
}

async function load() {
  loading.value = true
  try {
    organizations.value = await fetchOrganizations()
  } catch {
    organizations.value = []
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleDateString('zh-CN')
  } catch {
    return dateStr
  }
}

onMounted(load)
</script>

<style scoped>
.org-page {
  max-width: var(--content-max-width);
  margin: 0 auto;
}

.org-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-8);
}

.org-title {
  font-family: var(--font-heading);
  font-size: var(--text-3xl);
  font-weight: 700;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: var(--space-2);
}

.org-desc {
  font-size: var(--text-base);
  color: var(--color-muted-foreground);
}

.org-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--space-6);
}

.org-skeleton {
  height: 160px;
  border-radius: var(--radius-lg);
}

.org-card {
  background: var(--color-card);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.org-card:hover {
  box-shadow: var(--shadow-md), var(--glow-accent);
  transform: translateY(-2px);
  border-color: var(--color-secondary);
}

.org-card-header {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

.org-avatar {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-lg);
  background: var(--gradient-primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-heading);
  font-size: var(--text-xl);
  font-weight: 700;
  flex-shrink: 0;
}

.org-name-group {
  min-width: 0;
}

.org-name {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-foreground);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.org-owner {
  font-size: var(--text-xs);
  color: var(--color-muted-foreground);
}

.org-desc-text {
  font-size: var(--text-sm);
  color: var(--color-muted-foreground);
  line-height: 1.6;
  margin-bottom: var(--space-5);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: calc(1.6em * 2);
}

.org-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--color-border-light);
  padding-top: var(--space-4);
}

.org-meta {
  font-size: var(--text-xs);
  color: var(--color-muted-foreground);
}
</style>
