<template>
  <div class="org-detail">
    <!-- Loading -->
    <div v-if="loading" class="detail-loading">
      <el-skeleton animated style="height: 200px" />
    </div>

    <!-- Not found -->
    <EmptyState
      v-else-if="!org"
      type="error"
      title="组织未找到"
      description="组织可能已删除，或你没有访问权限"
      action-label="返回组织列表"
      @action="$router.push('/organizations')"
    />

    <template v-else>
      <!-- Org info header -->
      <section class="org-info">
        <div class="org-info-main">
          <div class="org-avatar">{{ org.name.charAt(0).toUpperCase() }}</div>
          <div class="org-info-text">
            <h1 class="org-name">{{ org.name }}</h1>
            <p class="org-description">{{ org.description || '暂无描述' }}</p>
            <div class="org-meta-row">
              <el-tag size="small" :type="roleTagType" effect="light">
                {{ orgRoleLabel(myRole) }}
              </el-tag>
              <span class="org-meta">
                所有者：{{ org.owner?.username || org.owner?.email || '未知' }}
              </span>
              <span class="org-meta">创建于 {{ formatDate(org.created_at) }}</span>
            </div>
          </div>
        </div>
        <div class="org-actions">
          <el-button v-if="canManage" :icon="Edit" @click="openEditDialog">
            编辑信息
          </el-button>
          <el-button v-if="isOwner" type="danger" plain :icon="Delete" @click="handleDeleteOrg">
            删除组织
          </el-button>
          <el-button v-if="!isOwner" @click="handleQuit">
            退出组织
          </el-button>
        </div>
      </section>

      <!-- Members -->
      <section class="members-section">
        <div class="section-header">
          <h2 class="section-title">成员管理（{{ members.length }}）</h2>
          <el-button v-if="canManage" type="primary" :icon="Plus" @click="openAddMember">
            添加成员
          </el-button>
        </div>

        <el-table :data="members" class="member-table" v-loading="membersLoading">
          <el-table-column label="成员" min-width="220">
            <template #default="{ row }">
              <div class="member-cell">
                <UserAvatar :email="row.user?.email || ''" />
                <div class="member-info">
                  <span class="member-name">
                    {{ row.user?.username || row.user?.email || `用户 #${row.user?.id ?? '?'}` }}
                  </span>
                  <span v-if="row.user?.email" class="member-email">{{ row.user.email }}</span>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="角色" width="160">
            <template #default="{ row }">
              <el-tag v-if="row.role === 'owner'" type="danger" effect="light">
                {{ orgRoleLabel(row.role) }}
              </el-tag>
              <el-select
                v-else-if="isOwner && row.role !== 'owner'"
                :model-value="row.role"
                size="small"
                style="width: 110px"
                @change="(role: any) => handleChangeRole(row, role)"
              >
                <el-option label="管理员" value="admin" />
                <el-option label="成员" value="member" />
              </el-select>
              <el-tag v-else :type="row.role === 'admin' ? 'warning' : 'info'" effect="light">
                {{ orgRoleLabel(row.role) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="加入时间" width="140">
            <template #default="{ row }">
              <span class="joined-at">{{ formatDate(row.joined_at) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" align="right">
            <template #default="{ row }">
              <el-button
                v-if="canManage && row.role !== 'owner'"
                size="small"
                type="danger"
                text
                @click="handleRemoveMember(row)"
              >
                移除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </section>

      <!-- Edit org dialog -->
      <el-dialog v-model="editDialogVisible" title="编辑组织" width="480px" :close-on-click-modal="false">
        <el-form ref="editFormRef" :model="editForm" :rules="editRules" label-width="80px">
          <el-form-item label="名称" prop="name">
            <el-input v-model="editForm.name" maxlength="100" show-word-limit />
          </el-form-item>
          <el-form-item label="描述" prop="description">
            <el-input v-model="editForm.description" type="textarea" :rows="3" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="handleSaveEdit">保存</el-button>
        </template>
      </el-dialog>

      <!-- Add member dialog -->
      <el-dialog v-model="addDialogVisible" title="添加成员" width="440px" :close-on-click-modal="false">
        <el-form ref="addFormRef" :model="addForm" :rules="addRules" label-width="80px">
          <el-form-item label="用户 ID" prop="user_id">
            <el-input-number v-model="addForm.user_id" :min="1" style="width: 100%" />
            <div class="form-hint">输入要添加的用户 ID（目前需由创建者告知）</div>
          </el-form-item>
          <el-form-item label="角色" prop="role">
            <el-radio-group v-model="addForm.role">
              <el-radio value="member">成员</el-radio>
              <el-radio value="admin">管理员</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="addDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="handleAddMember">添加</el-button>
        </template>
      </el-dialog>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Edit, Plus } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import {
  orgRoleLabel,
  type Organization,
  type OrganizationMember,
  type OrgRole,
} from '@/types/knowledge'
import {
  addMember,
  deleteOrganization,
  fetchMembers,
  fetchOrganization,
  quitOrganization,
  removeMember,
  updateMemberRole,
  updateOrganization,
} from '@/api/organization'
import { useAuthStore } from '@/stores/auth'
import EmptyState from '@/components/common/EmptyState.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'

const route = useRoute()
const authStore = useAuthStore()
const orgId = computed(() => parseInt(route.params.id as string))

const org = ref<Organization | null>(null)
const members = ref<OrganizationMember[]>([])
const loading = ref(false)
const membersLoading = ref(false)
const submitting = ref(false)

const editDialogVisible = ref(false)
const addDialogVisible = ref(false)
const editFormRef = ref<FormInstance>()
const addFormRef = ref<FormInstance>()
const editForm = ref({ name: '', description: '' })
const addForm = ref<{ user_id: number | undefined; role: OrgRole }>({ user_id: undefined, role: 'member' })

const editRules: FormRules = {
  name: [{ required: true, message: '请输入组织名称', trigger: 'blur' }],
}
const addRules: FormRules = {
  user_id: [{ required: true, message: '请输入用户 ID', trigger: 'blur' }],
}

/** 当前用户在本组织的角色 */
const myRole = computed<OrgRole | null>(() => {
  if (!authStore.user?.id) return null
  const me = members.value.find((m) => m.user?.id === authStore.user?.id)
  return me?.role || null
})

const isOwner = computed(() => myRole.value === 'owner')
const canManage = computed(() => myRole.value === 'owner' || myRole.value === 'admin')

const roleTagType = computed(() => {
  if (myRole.value === 'owner') return 'danger'
  if (myRole.value === 'admin') return 'warning'
  return 'info'
})

async function load() {
  loading.value = true
  try {
    org.value = await fetchOrganization(orgId.value)
  } catch {
    org.value = null
  } finally {
    loading.value = false
  }
  await loadMembers()
}

async function loadMembers() {
  membersLoading.value = true
  try {
    members.value = await fetchMembers(orgId.value)
  } catch {
    members.value = []
  } finally {
    membersLoading.value = false
  }
}

function openEditDialog() {
  if (!org.value) return
  editForm.value = { name: org.value.name, description: org.value.description || '' }
  editDialogVisible.value = true
}

async function handleSaveEdit() {
  if (!editFormRef.value) return
  const valid = await editFormRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    await updateOrganization(orgId.value, {
      name: editForm.value.name.trim(),
      description: editForm.value.description.trim(),
    })
    ElMessage.success('组织信息已更新')
    editDialogVisible.value = false
    await load()
  } catch {
    // 拦截器已提示
  } finally {
    submitting.value = false
  }
}

async function handleDeleteOrg() {
  try {
    await ElMessageBox.confirm(
      `确定删除组织「${org.value?.name}」吗？该组织下的知识库也会一并删除，且不可恢复。`,
      '删除确认',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }
    )
  } catch {
    return
  }
  try {
    await deleteOrganization(orgId.value)
    ElMessage.success('组织已删除')
    // 回到列表
    window.location.hash = '#/organizations'
  } catch {
    // 拦截器已提示
  }
}

async function handleQuit() {
  try {
    await ElMessageBox.confirm('确定退出该组织吗？', '退出确认', {
      type: 'warning',
      confirmButtonText: '退出',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  try {
    await quitOrganization(orgId.value)
    ElMessage.success('已退出组织')
    window.location.hash = '#/organizations'
  } catch {
    // 拦截器已提示
  }
}

function openAddMember() {
  addForm.value = { user_id: undefined, role: 'member' }
  addDialogVisible.value = true
}

async function handleAddMember() {
  if (!addFormRef.value) return
  const valid = await addFormRef.value.validate().catch(() => false)
  if (!valid || addForm.value.user_id === undefined) return
  submitting.value = true
  try {
    await addMember(orgId.value, addForm.value.user_id, addForm.value.role)
    ElMessage.success('成员已添加')
    addDialogVisible.value = false
    await loadMembers()
  } catch {
    // 拦截器已提示
  } finally {
    submitting.value = false
  }
}

async function handleChangeRole(row: OrganizationMember, role: OrgRole) {
  if (!row.user) return
  try {
    await updateMemberRole(orgId.value, row.user.id, role)
    ElMessage.success('角色已更新')
    await loadMembers()
  } catch {
    // 拦截器已提示
  }
}

async function handleRemoveMember(row: OrganizationMember) {
  if (!row.user) return
  try {
    await ElMessageBox.confirm(
      `确定移除成员「${row.user.username || row.user.email}」吗？`,
      '移除确认',
      { type: 'warning', confirmButtonText: '移除', cancelButtonText: '取消' }
    )
  } catch {
    return
  }
  try {
    await removeMember(orgId.value, row.user.id)
    ElMessage.success('成员已移除')
    await loadMembers()
  } catch {
    // 拦截器已提示
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
.org-detail {
  max-width: var(--content-max-width);
  margin: 0 auto;
}

.detail-loading {
  padding: var(--space-8);
}

/* Org info */
.org-info {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-6);
  margin-bottom: var(--space-8);
}

.org-info-main {
  display: flex;
  gap: var(--space-5);
  min-width: 0;
}

.org-avatar {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-xl);
  background: var(--gradient-primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  font-weight: 700;
  flex-shrink: 0;
}

.org-name {
  font-family: var(--font-heading);
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--color-foreground);
  margin-bottom: var(--space-2);
}

.org-description {
  font-size: var(--text-base);
  color: var(--color-muted-foreground);
  margin-bottom: var(--space-3);
}

.org-meta-row {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  flex-wrap: wrap;
}

.org-meta {
  font-size: var(--text-sm);
  color: var(--color-muted-foreground);
}

.org-actions {
  display: flex;
  gap: var(--space-3);
  flex-shrink: 0;
}

/* Members */
.members-section {
  background: var(--color-card);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
}

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

.member-table {
  width: 100%;
}

.member-cell {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.member-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.member-name {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-foreground);
}

.member-email {
  font-size: var(--text-xs);
  color: var(--color-muted-foreground);
}

.joined-at {
  font-size: var(--text-sm);
  color: var(--color-muted-foreground);
}

.form-hint {
  font-size: var(--text-xs);
  color: var(--color-muted-foreground);
  margin-top: var(--space-2);
  line-height: 1.5;
}

@media (max-width: 768px) {
  .org-info {
    flex-direction: column;
  }
}
</style>
