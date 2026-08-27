<template>
  <div class="admin-page">
    <header class="admin-page__head">
      <div>
        <span class="eyebrow">管理员</span>
        <h1 class="display-2 admin-page__title">账号申请审核</h1>
        <p class="admin-page__lede">审批用户的注册申请。通过后会生成邀请链接发送给对方。</p>
      </div>
    </header>

    <section class="stats-row">
      <article class="stat-card">
        <span class="eyebrow">全部</span>
        <div class="stat-card__value mono">{{ stats.total }}</div>
      </article>
      <article class="stat-card">
        <span class="eyebrow">待处理</span>
        <div class="stat-card__value mono">{{ stats.pending }}</div>
      </article>
      <article class="stat-card">
        <span class="eyebrow">已通过</span>
        <div class="stat-card__value mono">{{ stats.approved }}</div>
      </article>
    </section>

    <div class="filter-bar">
      <div class="filter-bar__chips">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="chip"
          :class="{ 'chip--active': activeFilter === tab.key }"
          @click="activeFilter = tab.key"
        >
          {{ tab.label }}
          <span class="chip__count mono">{{ tab.count }}</span>
        </button>
      </div>
      <button class="btn btn--ghost btn--sm" style="margin-left: auto" @click="load">
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M3 12a9 9 0 0 1 9-9 9 9 0 0 1 6.7 3M21 12a9 9 0 0 1-9 9 9 9 0 0 1-6.7-3M3 4v5h5M21 20v-5h-5" stroke-linecap="round" stroke-linejoin="round"/></svg>
        刷新
      </button>
    </div>

    <div v-if="loading" class="loading">加载中…</div>

    <EmptyState
      v-else-if="filtered.length === 0"
      :title="requests.length === 0 ? '还没有申请' : '没有匹配的申请'"
      :description="requests.length === 0 ? '等待用户提交注册申请' : '尝试其他筛选'"
    />

    <ul v-else class="request-list">
      <li v-for="r in filtered" :key="r.id" class="request-row">
        <div class="request-row__id mono">#{{ String(r.id).padStart(3, '0') }}</div>
        <div class="request-row__main">
          <div class="request-row__email">
            <span>{{ r.email }}</span>
            <span class="badge" :class="`badge--${statusVariant(r.status)}`">
              <span class="dot" /> {{ statusLabel(r.status) }}
            </span>
          </div>
          <p class="request-row__reason">{{ r.reason || '无理由' }}</p>
        </div>
        <div class="request-row__action">
          <button
            v-if="!r.status || r.status === 'pending'"
            class="btn btn--primary btn--sm"
            @click="approve(r.id)"
          >通过</button>
          <span v-else class="muted mono">已处理</span>
        </div>
      </li>
    </ul>

    <!-- Result modal -->
    <transition name="fade">
      <div v-if="approveResult" class="modal-backdrop" @click.self="approveResult = null">
        <div class="result-modal">
          <div class="result-modal__icon">
            <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="m8 12 3 3 5-6" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </div>
          <h3 class="result-modal__title">已通过申请</h3>
          <p class="result-modal__desc">邀请链接已发送到 <strong>{{ approveResult.email }}</strong></p>
          <div class="result-modal__url">
            <code class="mono">{{ approveResult.register_url }}</code>
          </div>
          <button class="btn btn--primary" @click="approveResult = null">完成</button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { approveRequest, listRequests } from '@/api/auth'
import EmptyState from '@/components/common/EmptyState.vue'
import type { ApproveResponse, UserRequestOutput } from '@/types/api'

const requests = ref<UserRequestOutput[]>([])
const loading = ref(true)
const activeFilter = ref<'all' | 'pending' | 'approved'>('pending')
const approveResult = ref<ApproveResponse | null>(null)

async function load() {
  loading.value = true
  try {
    requests.value = await listRequests()
  } catch {
    requests.value = []
  } finally {
    loading.value = false
  }
}
onMounted(load)

const stats = computed(() => ({
  total: requests.value.length,
  pending: requests.value.filter((r) => !r.status || r.status === 'pending').length,
  approved: requests.value.filter((r) => r.status === 'approved').length,
}))

const tabs = computed(() => [
  { key: 'pending' as const, label: '待处理', count: stats.value.pending },
  { key: 'approved' as const, label: '已通过', count: stats.value.approved },
  { key: 'all' as const, label: '全部', count: stats.value.total },
])

const filtered = computed(() => {
  if (activeFilter.value === 'all') return requests.value
  if (activeFilter.value === 'pending') return requests.value.filter((r) => !r.status || r.status === 'pending')
  return requests.value.filter((r) => r.status === 'approved')
})

async function approve(id: number) {
  try {
    approveResult.value = await approveRequest(id)
    await load()
  } catch {
    /* ignore */
  }
}

function statusLabel(s: string | null) {
  if (!s || s === 'pending') return '待处理'
  if (s === 'approved') return '已通过'
  if (s === 'rejected') return '已拒绝'
  return s
}

function statusVariant(s: string | null): string {
  if (!s || s === 'pending') return 'warning'
  if (s === 'approved') return 'success'
  if (s === 'rejected') return 'danger'
  return ''
}
</script>

<style lang="scss" scoped>
@use '@/styles/tokens' as *;

.admin-page {
  &__head {
    margin-bottom: $s-6;
    padding-bottom: $s-6;
    border-bottom: 1px solid $border-subtle;
  }
  &__title { margin-top: $s-3; }
  &__lede {
    margin-top: $s-3;
    color: $text-secondary;
    font-size: $fs-15;
    max-width: 520px;
  }
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: $s-4;
  margin-bottom: $s-6;
}

.stat-card {
  background: $bg-surface;
  border: 1px solid $border-subtle;
  border-radius: $r-lg;
  padding: $s-5;
  display: flex;
  flex-direction: column;
  gap: $s-3;

  .eyebrow { color: $accent; }
  &__value {
    font-family: $font-display;
    font-size: $fs-32;
    font-weight: $fw-semibold;
    line-height: 1;
  }
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: $s-4;
  margin-bottom: $s-5;

  &__chips {
    display: flex;
    gap: $s-1;
  }
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: $s-2;
  padding: 6px $s-3;
  border-radius: $r-sm;
  background: transparent;
  border: none;
  color: $text-secondary;
  font-size: $fs-13;
  cursor: pointer;
  transition: all $dur-base $ease-out;
  &:hover { color: $text-primary; background: $bg-surface; }
  &--active {
    color: $accent;
    background: $accent-soft;
    .chip__count { color: $accent; }
  }
  &__count {
    font-size: $fs-12;
    color: $text-tertiary;
    padding: 0 4px;
  }
}

.loading {
  text-align: center;
  padding: $s-10;
  color: $text-tertiary;
}

.request-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: $s-2;
}

.request-row {
  display: flex;
  align-items: center;
  gap: $s-4;
  padding: $s-4 $s-5;
  background: $bg-surface;
  border: 1px solid $border-subtle;
  border-radius: $r-md;
  transition: all $dur-base $ease-out;

  &:hover { border-color: $border-strong; background: $bg-elevated; }

  &__id {
    color: $accent;
    font-size: $fs-13;
    min-width: 50px;
  }
  &__main {
    flex: 1;
    min-width: 0;
  }
  &__email {
    display: flex;
    align-items: center;
    gap: $s-2;
    font-size: $fs-14;
    color: $text-primary;
    font-weight: $fw-medium;
    margin-bottom: $s-1;
  }
  &__reason {
    font-size: $fs-13;
    color: $text-secondary;
    line-height: $lh-snug;
  }
  &__action { flex-shrink: 0; }
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
}

.result-modal {
  width: 440px;
  background: $bg-surface;
  border: 1px solid $border-strong;
  border-radius: $r-lg;
  padding: $s-6;
  box-shadow: $shadow-lg;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $s-3;

  &__icon {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: $success-soft;
    color: $success;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: $s-2;
  }
  &__title {
    font-family: $font-display;
    font-size: $fs-20;
    font-weight: $fw-semibold;
  }
  &__desc {
    color: $text-secondary;
    font-size: $fs-14;
    text-align: center;
    strong { color: $accent; }
  }
  &__url {
    width: 100%;
    padding: $s-3;
    background: $bg-inset;
    border: 1px solid $border-subtle;
    border-radius: $r-md;
    code {
      font-size: $fs-12;
      color: $text-secondary;
      word-break: break-all;
    }
  }
}

.fade-enter-active, .fade-leave-active { transition: opacity $dur-base $ease-out; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>