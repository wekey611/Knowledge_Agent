<template>
  <div class="org-page">
    <header class="org-page__head">
      <div>
        <span class="eyebrow">组织</span>
        <h1 class="display-2 org-page__title">我的组织</h1>
        <p class="org-page__lede">创建组织，与团队协作共享知识库。</p>
      </div>
      <button class="btn btn--primary" @click="createOpen = true">
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14" stroke-linecap="round"/></svg>
        创建组织
      </button>
    </header>

    <div v-if="loading" class="grid">
      <div v-for="i in 4" :key="i" class="skel-card" />
    </div>

    <EmptyState
      v-else-if="orgs.length === 0"
      title="还没有组织"
      description="创建一个组织开始协作。"
    >
      <template #action>
        <button class="btn btn--primary" @click="createOpen = true">创建组织</button>
      </template>
    </EmptyState>

    <div v-else class="grid">
      <article v-for="o in orgs" :key="o.id" class="org-card" @click="$router.push(`/organizations/${o.id}`)">
        <div class="org-card__head">
          <div class="org-card__avatar">{{ o.name.charAt(0).toUpperCase() }}</div>
          <div class="org-card__head-text">
            <h3 class="org-card__name">{{ o.name }}</h3>
            <p class="org-card__desc">{{ o.description || '无描述' }}</p>
          </div>
        </div>
        <div class="org-card__footer">
          <span class="meta-item">
            <span class="eyebrow">成员</span>
            <span class="mono">{{ o.members?.length || 0 }}</span>
          </span>
          <span class="meta-item">
            <span class="eyebrow">所有者</span>
            <span class="mono">{{ o.owner?.username || o.owner?.email || '—' }}</span>
          </span>
          <span class="meta-item">
            <span class="eyebrow">创建</span>
            <span class="mono faint">{{ formatDate(o.created_at) }}</span>
          </span>
        </div>
      </article>
    </div>

    <!-- Create modal -->
    <transition name="fade">
      <div v-if="createOpen" class="modal-backdrop" @click.self="createOpen = false">
        <div class="modal">
          <header class="modal__head">
            <div>
              <span class="eyebrow">新建</span>
              <h2 class="modal__title">创建组织</h2>
            </div>
            <button class="btn btn--icon btn--ghost btn--sm" @click="createOpen = false">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M6 6l12 12M6 18L18 6" stroke-linecap="round"/></svg>
            </button>
          </header>
          <form @submit.prevent="handleCreate" class="modal__body">
            <div class="field">
              <label class="field__label">名称</label>
              <input v-model="form.name" class="input" placeholder="组织名称" maxlength="100" required />
            </div>
            <div class="field">
              <label class="field__label">描述</label>
              <textarea v-model="form.description" class="textarea" rows="3" required />
            </div>
            <div v-if="error" class="form-error">{{ error }}</div>
            <footer class="modal__foot">
              <button type="button" class="btn btn--ghost" @click="createOpen = false">取消</button>
              <button type="submit" class="btn btn--primary" :disabled="loading">
                {{ loading ? '创建中…' : '创建' }}
              </button>
            </footer>
          </form>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { fetchOrganizations, createOrganization } from '@/api/organization'
import EmptyState from '@/components/common/EmptyState.vue'
import type { Organization } from '@/types/knowledge'

const router = useRouter()
const orgs = ref<Organization[]>([])
const loading = ref(true)
const createOpen = ref(false)
const error = ref('')

const form = reactive({ name: '', description: '' })

onMounted(async () => {
  try {
    orgs.value = await fetchOrganizations()
  } finally {
    loading.value = false
  }
})

async function handleCreate() {
  error.value = ''
  loading.value = true
  try {
    const created = await createOrganization({ name: form.name, description: form.description })
    createOpen.value = false
    router.push(`/organizations/${created.id}`)
  } catch (e: any) {
    error.value = e?.response?.data?.detail || '创建失败'
  } finally {
    loading.value = false
  }
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

.org-page {
  &__head {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: $s-4;
    margin-bottom: $s-6;
    padding-bottom: $s-6;
    border-bottom: 1px solid $border-subtle;
  }
  &__title { margin-top: $s-3; }
  &__lede {
    margin-top: $s-3;
    color: $text-secondary;
    font-size: $fs-15;
    max-width: 460px;
  }
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: $s-4;
}

.org-card {
  display: flex;
  flex-direction: column;
  gap: $s-4;
  background: $bg-surface;
  border: 1px solid $border-subtle;
  border-radius: $r-lg;
  padding: $s-5;
  cursor: pointer;
  transition: all $dur-base $ease-out;

  &:hover {
    border-color: $border-strong;
    background: $bg-elevated;
    transform: translateY(-2px);
  }

  &__head {
    display: flex;
    align-items: flex-start;
    gap: $s-3;
  }
  &__avatar {
    width: 44px;
    height: 44px;
    flex-shrink: 0;
    border-radius: $r-md;
    background: $accent;
    color: $text-inverse;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: $font-display;
    font-size: $fs-20;
    font-weight: $fw-semibold;
  }
  &__head-text { flex: 1; min-width: 0; }
  &__name {
    font-family: $font-display;
    font-size: $fs-20;
    font-weight: $fw-semibold;
    color: $text-primary;
    margin-bottom: $s-1;
  }
  &__desc {
    font-size: $fs-13;
    color: $text-secondary;
    line-height: $lh-snug;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  &__footer {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: $s-3;
    padding-top: $s-3;
    border-top: 1px solid $border-subtle;
  }
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: $fs-13;
  color: $text-primary;
  .eyebrow { color: $text-tertiary; }
}

.skel-card {
  height: 180px;
  background: linear-gradient(90deg, $bg-surface 0%, $bg-elevated 50%, $bg-surface 100%);
  background-size: 200% 100%;
  border-radius: $r-lg;
  animation: shimmer 1.6s linear infinite;
  border: 1px solid $border-subtle;
}
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

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
  max-width: 480px;
  background: $bg-surface;
  border: 1px solid $border-strong;
  border-radius: $r-lg;
  box-shadow: $shadow-lg;

  &__head {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    padding: $s-5 $s-6 $s-4;
    border-bottom: 1px solid $border-subtle;
  }
  &__title {
    margin-top: $s-2;
    font-family: $font-display;
    font-size: $fs-24;
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
}

.form-error {
  padding: $s-3 $s-4;
  background: $danger-soft;
  color: $danger;
  border-radius: $r-md;
  font-size: $fs-13;
}

.fade-enter-active, .fade-leave-active { transition: opacity $dur-base $ease-out; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>