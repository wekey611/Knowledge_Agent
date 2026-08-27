<template>
  <div class="org-detail" v-if="org">
    <header class="org-detail__head">
      <button class="back-btn" @click="$router.push('/organizations')">
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6"><path d="m15 6-6 6 6 6" stroke-linecap="round" stroke-linejoin="round"/></svg>
        <span>组织</span>
      </button>
      <div class="org-detail__main">
        <div class="org-detail__avatar">{{ org.name.charAt(0).toUpperCase() }}</div>
        <div class="org-detail__text">
          <h1 class="org-detail__name">{{ org.name }}</h1>
          <p class="org-detail__desc">{{ org.description || '无描述' }}</p>
          <div class="org-detail__meta">
            <span class="badge" :class="`badge--${myRoleVariant}`">
              <span class="dot" /> {{ orgRoleLabel(myRole) }}
            </span>
            <span class="muted">所有者：{{ org.owner?.username || org.owner?.email || '—' }}</span>
            <span class="faint mono">{{ formatDate(org.created_at) }}</span>
          </div>
        </div>
      </div>
      <div class="org-detail__actions">
        <button v-if="canManage" class="btn btn--ghost" @click="startEdit">编辑信息</button>
        <button v-if="isOwner" class="btn btn--danger" @click="handleDeleteOrg">删除组织</button>
        <button v-if="!isOwner" class="btn btn--ghost" @click="handleQuit">退出组织</button>
      </div>
    </header>

    <!-- Members -->
    <section class="members-section">
      <div class="section-head">
        <div>
          <span class="eyebrow">成员</span>
          <h2 class="section-head__title">{{ members.length }} 人</h2>
        </div>
        <button v-if="canManage" class="btn btn--primary" @click="addOpen = true">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14" stroke-linecap="round"/></svg>
          添加成员
        </button>
      </div>

      <div v-if="membersLoading" class="members-list">
        <div v-for="i in 3" :key="i" class="member-row member-row--skel" />
      </div>
      <div v-else class="members-list">
        <div v-for="m in members" :key="m.user?.id" class="member-row">
          <div class="member-row__avatar">{{ (m.user?.email || m.user?.username || '?').charAt(0).toUpperCase() }}</div>
          <div class="member-row__main">
            <span class="member-row__name">{{ m.user?.username || m.user?.email || `用户 #${m.user?.id}` }}</span>
            <span class="member-row__email">{{ m.user?.email }}</span>
          </div>
          <div class="member-row__role">
            <select
              v-if="isOwner && m.role !== 'owner'"
              :value="m.role"
              class="select"
              @change="(e) => handleChangeRole(m, (e.target as HTMLSelectElement).value as OrgRole)"
            >
              <option value="admin">管理员</option>
              <option value="member">成员</option>
            </select>
            <span v-else class="badge" :class="`badge--${roleVariant(m.role)}`">
              <span class="dot" /> {{ orgRoleLabel(m.role) }}
            </span>
          </div>
          <span class="member-row__joined faint mono">{{ formatDate(m.joined_at) }}</span>
          <button v-if="canManage && m.role !== 'owner'" class="btn btn--ghost btn--sm" @click="handleRemove(m)">移除</button>
        </div>
      </div>
    </section>

    <!-- Edit modal -->
    <transition name="fade">
      <div v-if="editOpen" class="modal-backdrop" @click.self="editOpen = false">
        <div class="modal">
          <header class="modal__head">
            <h2 class="modal__title">编辑组织</h2>
            <button class="btn btn--icon btn--ghost btn--sm" @click="editOpen = false">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M6 6l12 12M6 18L18 6" stroke-linecap="round"/></svg>
            </button>
          </header>
          <form @submit.prevent="handleSaveEdit" class="modal__body">
            <div class="field">
              <label class="field__label">名称</label>
              <input v-model="editForm.name" class="input" maxlength="100" required />
            </div>
            <div class="field">
              <label class="field__label">描述</label>
              <textarea v-model="editForm.description" class="textarea" rows="3" required />
            </div>
            <footer class="modal__foot">
              <button type="button" class="btn btn--ghost" @click="editOpen = false">取消</button>
              <button type="submit" class="btn btn--primary" :disabled="submitting">
                {{ submitting ? '保存中…' : '保存' }}
              </button>
            </footer>
          </form>
        </div>
      </div>
    </transition>

    <!-- Add member modal -->
    <transition name="fade">
      <div v-if="addOpen" class="modal-backdrop" @click.self="addOpen = false">
        <div class="modal">
          <header class="modal__head">
            <h2 class="modal__title">添加成员</h2>
            <button class="btn btn--icon btn--ghost btn--sm" @click="addOpen = false">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M6 6l12 12M6 18L18 6" stroke-linecap="round"/></svg>
            </button>
          </header>
          <form @submit.prevent="handleAddMember" class="modal__body">
            <div class="field">
              <label class="field__label">用户 ID</label>
              <input v-model.number="addForm.user_id" type="number" class="input" min="1" required />
              <span class="field__hint">输入要添加的用户 ID（需由创建者提供）</span>
            </div>
            <div class="field">
              <label class="field__label">角色</label>
              <div class="radio-row">
                <label class="radio-card" :class="{ 'radio-card--active': addForm.role === 'member' }">
                  <input type="radio" v-model="addForm.role" value="member" />
                  <span class="radio-card__title">成员</span>
                </label>
                <label class="radio-card" :class="{ 'radio-card--active': addForm.role === 'admin' }">
                  <input type="radio" v-model="addForm.role" value="admin" />
                  <span class="radio-card__title">管理员</span>
                </label>
              </div>
            </div>
            <footer class="modal__foot">
              <button type="button" class="btn btn--ghost" @click="addOpen = false">取消</button>
              <button type="submit" class="btn btn--primary" :disabled="submitting">
                {{ submitting ? '添加中…' : '添加' }}
              </button>
            </footer>
          </form>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { addMember, deleteOrganization, fetchMembers, fetchOrganization, quitOrganization, removeMember, updateMemberRole, updateOrganization } from '@/api/organization'
import { useAuthStore } from '@/stores/auth'
import { orgRoleLabel } from '@/types/knowledge'
import type { Organization, OrganizationMember, OrgRole } from '@/types/knowledge'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const orgId = computed(() => Number(route.params.id))

const org = ref<Organization | null>(null)
const members = ref<OrganizationMember[]>([])
const membersLoading = ref(true)
const submitting = ref(false)
const editOpen = ref(false)
const addOpen = ref(false)

const editForm = reactive({ name: '', description: '' })
const addForm = reactive<{ user_id: number | null; role: OrgRole }>({ user_id: null, role: 'member' })

const myRole = computed<OrgRole | null>(() => {
  if (!auth.user?.id) return null
  return members.value.find((m) => m.user?.id === auth.user?.id)?.role || null
})
const isOwner = computed(() => myRole.value === 'owner')
const canManage = computed(() => myRole.value === 'owner' || myRole.value === 'admin')

const myRoleVariant = computed(() => roleVariant(myRole.value))

async function load() {
  try {
    org.value = await fetchOrganization(orgId.value)
  } catch {
    org.value = null
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

watch(orgId, load)
onMounted(load)

function startEdit() {
  if (!org.value) return
  editForm.name = org.value.name
  editForm.description = org.value.description || ''
  editOpen.value = true
}

async function handleSaveEdit() {
  submitting.value = true
  try {
    await updateOrganization(orgId.value, { name: editForm.name.trim(), description: editForm.description.trim() })
    editOpen.value = false
    await load()
  } catch {
    /* interceptor */
  } finally {
    submitting.value = false
  }
}

async function handleDeleteOrg() {
  if (!confirm(`确定删除组织「${org.value?.name}」吗？该操作不可撤销。`)) return
  try {
    await deleteOrganization(orgId.value)
    router.push('/organizations')
  } catch {
    /* */
  }
}

async function handleQuit() {
  if (!confirm('确定退出该组织？')) return
  try {
    await quitOrganization(orgId.value)
    router.push('/organizations')
  } catch {
    /* */
  }
}

async function handleAddMember() {
  if (!addForm.user_id) return
  submitting.value = true
  try {
    await addMember(orgId.value, addForm.user_id, addForm.role)
    addOpen.value = false
    await loadMembers()
  } catch {
    /* */
  } finally {
    submitting.value = false
  }
}

async function handleChangeRole(m: OrganizationMember, role: OrgRole) {
  if (!m.user) return
  try {
    await updateMemberRole(orgId.value, m.user.id, role)
    await loadMembers()
  } catch {
    /* */
  }
}

async function handleRemove(m: OrganizationMember) {
  if (!m.user) return
  if (!confirm(`确定移除成员「${m.user.username || m.user.email}」？`)) return
  try {
    await removeMember(orgId.value, m.user.id)
    await loadMembers()
  } catch {
    /* */
  }
}

function roleVariant(role: string | null): string {
  if (role === 'owner') return 'danger'
  if (role === 'admin') return 'warning'
  return ''
}

function formatDate(iso: string) {
  try {
    return new Date(iso).toLocaleDateString('zh-CN', { dateStyle: 'short' })
  } catch {
    return iso
  }
}
</script>

<style lang="scss" scoped>
@use '@/styles/tokens' as *;

.org-detail {
  &__head {
    display: flex;
    align-items: flex-start;
    gap: $s-3;
    margin-bottom: $s-8;
    padding-bottom: $s-6;
    border-bottom: 1px solid $border-subtle;
  }
  &__main {
    flex: 1;
    display: flex;
    align-items: flex-start;
    gap: $s-4;
    margin-top: $s-4;
  }
  &__avatar {
    width: 64px;
    height: 64px;
    border-radius: $r-lg;
    background: $accent;
    color: $text-inverse;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: $font-display;
    font-size: $fs-24;
    font-weight: $fw-semibold;
    flex-shrink: 0;
  }
  &__name {
    font-family: $font-display;
    font-size: $fs-32;
    font-weight: $fw-semibold;
    letter-spacing: -0.015em;
    margin-bottom: $s-2;
  }
  &__desc {
    color: $text-secondary;
    font-size: $fs-15;
    margin-bottom: $s-3;
  }
  &__meta {
    display: flex;
    align-items: center;
    gap: $s-3;
    font-size: $fs-13;
    flex-wrap: wrap;
  }
  &__actions {
    display: flex;
    gap: $s-2;
    flex-shrink: 0;
    margin-top: $s-4;
  }
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: $s-2;
  padding: $s-2 $s-3;
  border-radius: $r-md;
  background: transparent;
  border: 1px solid $border-subtle;
  color: $text-secondary;
  font-size: $fs-13;
  cursor: pointer;
  transition: all $dur-base $ease-out;
  &:hover { background: $bg-surface; color: $text-primary; }
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: $s-4;

  .eyebrow { display: block; margin-bottom: $s-1; }
  &__title {
    font-family: $font-body;
    font-weight: $fw-semibold;
    font-size: $fs-17;
    color: $text-primary;
  }
}

.members-section {
  background: $bg-surface;
  border: 1px solid $border-subtle;
  border-radius: $r-lg;
  padding: $s-6;
}

.members-list {
  display: flex;
  flex-direction: column;
}

.member-row {
  display: grid;
  grid-template-columns: auto 1fr auto auto auto;
  align-items: center;
  gap: $s-4;
  padding: $s-3 $s-2;
  border-bottom: 1px solid $border-subtle;
  font-size: $fs-13;

  &:last-child { border-bottom: none; }
  &:hover { background: $bg-elevated; }
  &--skel {
    height: 56px;
    background: linear-gradient(90deg, $bg-surface 0%, $bg-elevated 50%, $bg-surface 100%);
    background-size: 200% 100%;
    animation: shimmer 1.6s linear infinite;
  }

  &__avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: $bg-elevated;
    color: $accent;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: $font-display;
    font-weight: $fw-semibold;
    font-size: $fs-14;
  }
  &__main {
    display: flex;
    flex-direction: column;
    min-width: 0;
  }
  &__name {
    color: $text-primary;
    font-weight: $fw-medium;
  }
  &__email {
    color: $text-tertiary;
    font-size: $fs-12;
  }
  &__joined {
    min-width: 90px;
    text-align: right;
  }
}

.select {
  height: 28px;
  padding: 0 $s-2;
  border-radius: $r-sm;
  background: $bg-inset;
  border: 1px solid $border-subtle;
  color: $text-primary;
  font-size: $fs-13;
  cursor: pointer;
  &:hover { border-color: $border-strong; }
  &:focus { outline: none; border-color: $accent; }
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: $s-6;
}

.modal {
  width: 100%;
  max-width: 440px;
  background: $bg-surface;
  border: 1px solid $border-strong;
  border-radius: $r-lg;
  box-shadow: $shadow-lg;

  &__head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: $s-5 $s-6 $s-4;
    border-bottom: 1px solid $border-subtle;
  }
  &__title {
    font-family: $font-display;
    font-size: $fs-20;
    font-weight: $fw-semibold;
  }
  &__body {
    padding: $s-5 $s-6;
    display: flex;
    flex-direction: column;
    gap: $s-4;
  }
  &__foot {
    display: flex;
    justify-content: flex-end;
    gap: $s-2;
    padding-top: $s-3;
    border-top: 1px solid $border-subtle;
    margin-top: $s-2;
  }
}

.field {
  display: flex;
  flex-direction: column;
  gap: $s-2;
  &__label {
    font-size: $fs-13;
    font-weight: $fw-medium;
    color: $text-secondary;
  }
  &__hint {
    font-size: $fs-12;
    color: $text-tertiary;
  }
}

.radio-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: $s-2;
}

.radio-card {
  position: relative;
  padding: $s-3;
  background: $bg-inset;
  border: 1px solid $border-subtle;
  border-radius: $r-md;
  cursor: pointer;
  text-align: center;
  transition: all $dur-base $ease-out;

  input { position: absolute; opacity: 0; }

  &:hover { border-color: $border-strong; }
  &--active {
    border-color: $accent;
    background: $accent-soft;
  }

  &__title {
    font-size: $fs-14;
    font-weight: $fw-medium;
    color: $text-primary;
  }
}

@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
.fade-enter-active, .fade-leave-active { transition: opacity $dur-base $ease-out; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>