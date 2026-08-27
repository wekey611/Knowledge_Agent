<template>
  <div class="kb-list-page">
    <header class="kb-list-page__head">
      <div>
        <span class="eyebrow">知识库</span>
        <h1 class="display-2 kb-list-page__title">所有知识库</h1>
        <p class="kb-list-page__lede">
          管理个人、组织与公开的知识库；点击进入对话或文档管理。
        </p>
      </div>
      <button class="btn btn--primary" @click="createOpen = true">
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14" stroke-linecap="round"/></svg>
        新建知识库
      </button>
    </header>

    <!-- Filter bar -->
    <div class="filter-bar">
      <div class="filter-bar__search">
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6">
          <circle cx="11" cy="11" r="7" />
          <path d="m20 20-3.5-3.5" stroke-linecap="round" />
        </svg>
        <input v-model="query" class="filter-bar__input" placeholder="搜索名称或描述" />
      </div>
      <div class="filter-bar__chips">
        <button
          v-for="f in filters"
          :key="f.value"
          class="chip"
          :class="{ 'chip--active': scope === f.value }"
          @click="scope = f.value"
        >
          {{ f.label }}
          <span class="chip__count mono">{{ countByScope[f.value] }}</span>
        </button>
      </div>
      <div class="filter-bar__view">
        <button
          class="view-btn"
          :class="{ 'view-btn--active': view === 'grid' }"
          @click="view = 'grid'"
          title="网格视图"
        >
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>
        </button>
        <button
          class="view-btn"
          :class="{ 'view-btn--active': view === 'list' }"
          @click="view = 'list'"
          title="列表视图"
        >
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6"><line x1="3" y1="6" x2="21" y2="6" stroke-linecap="round"/><line x1="3" y1="12" x2="21" y2="12" stroke-linecap="round"/><line x1="3" y1="18" x2="21" y2="18" stroke-linecap="round"/></svg>
        </button>
      </div>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" :class="['grid', view === 'list' && 'grid--list']">
      <div v-for="i in 6" :key="i" class="skel-card" />
    </div>

    <!-- Empty state -->
    <EmptyState
      v-else-if="filtered.length === 0"
      :title="bases.length === 0 ? '还没有知识库' : '没有匹配的知识库'"
      :description="bases.length === 0 ? '从一个知识库开始吧。' : '试试其他关键字或范围筛选。'"
    >
      <template v-if="bases.length === 0" #action>
        <button class="btn btn--primary" @click="createOpen = true">新建第一个知识库</button>
      </template>
    </EmptyState>

    <!-- Grid view -->
    <div v-else-if="view === 'grid'" class="grid">
      <article
        v-for="kb in filtered"
        :key="kb.id"
        class="kb-card"
        @click="$router.push(`/knowledge/${kb.id}`)"
      >
        <header class="kb-card__head">
          <span class="kb-card__index mono">#{{ String(kb.id).padStart(3, '0') }}</span>
          <span class="badge" :class="`badge--${scopeVariant(kb.scope)}`">
            <span class="dot" /> {{ SCOPE_LABELS[kb.scope] }}
          </span>
        </header>

        <h3 class="kb-card__name">{{ kb.name }}</h3>
        <p class="kb-card__desc">{{ kb.description || '无描述' }}</p>

        <div class="kb-card__meta">
          <StatusDot :status="kb.status" />
          <span class="muted">{{ KB_STATUS_LABELS[kb.status] }}</span>
        </div>

        <footer class="kb-card__footer">
          <div class="kb-card__stat">
            <span class="kb-card__stat-num mono">{{ kb.document_count }}</span>
            <span class="kb-card__stat-label">文档</span>
          </div>
          <div class="kb-card__stat">
            <span class="kb-card__stat-num mono">{{ formatTime(kb.created_at) }}</span>
            <span class="kb-card__stat-label">创建</span>
          </div>
          <span class="kb-card__arrow">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6"><path d="m9 6 6 6-6 6" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </span>
        </footer>
      </article>
    </div>

    <!-- List view -->
    <div v-else class="table">
      <div class="table__head">
        <span>名称</span>
        <span>范围</span>
        <span>状态</span>
        <span class="num">文档</span>
        <span class="num">创建</span>
        <span></span>
      </div>
      <div
        v-for="kb in filtered"
        :key="kb.id"
        class="table__row"
        @click="$router.push(`/knowledge/${kb.id}`)"
      >
        <div class="table__cell table__cell--main">
          <span class="mono faint">#{{ String(kb.id).padStart(3, '0') }}</span>
          <span class="table__name">{{ kb.name }}</span>
        </div>
        <div class="table__cell">
          <span class="badge" :class="`badge--${scopeVariant(kb.scope)}`">
            <span class="dot" /> {{ SCOPE_LABELS[kb.scope] }}
          </span>
        </div>
        <div class="table__cell">
          <span class="table__status">
            <StatusDot :status="kb.status" />
            <span class="muted">{{ KB_STATUS_LABELS[kb.status] }}</span>
          </span>
        </div>
        <div class="table__cell num mono">{{ kb.document_count }}</div>
        <div class="table__cell num mono faint">{{ formatTime(kb.created_at) }}</div>
        <div class="table__cell table__cell--end">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6" class="faint"><path d="m9 6 6 6-6 6" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </div>
      </div>
    </div>

    <!-- Create modal -->
    <KnowledgeBaseFormDialog v-model="createOpen" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { fetchKnowledgeBases } from '@/api/knowledge'
import EmptyState from '@/components/common/EmptyState.vue'
import StatusDot from '@/components/common/StatusDot.vue'
import KnowledgeBaseFormDialog from '@/components/knowledge/KnowledgeBaseFormDialog.vue'
import { KB_STATUS_LABELS, SCOPE_LABELS } from '@/types/knowledge'
import type { KnowledgeBaseSimple, KnowledgeScope } from '@/types/knowledge'

const bases = ref<KnowledgeBaseSimple[]>([])
const loading = ref(true)
const query = ref('')
const scope = ref<'all' | KnowledgeScope>('all')
const view = ref<'grid' | 'list'>('grid')
const createOpen = ref(false)

const filters: { value: 'all' | KnowledgeScope; label: string }[] = [
  { value: 'all', label: '全部' },
  { value: 'personal', label: '个人' },
  { value: 'org', label: '组织' },
  { value: 'public', label: '公开' },
]

onMounted(async () => {
  try {
    const res = await fetchKnowledgeBases()
    bases.value = res.data
  } finally {
    loading.value = false
  }
})

const countByScope = computed(() => ({
  all: bases.value.length,
  personal: bases.value.filter((k) => k.scope === 'personal').length,
  org: bases.value.filter((k) => k.scope === 'org').length,
  public: bases.value.filter((k) => k.scope === 'public').length,
}))

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  return bases.value.filter((k) => {
    if (scope.value !== 'all' && k.scope !== scope.value) return false
    if (q && !k.name.toLowerCase().includes(q) && !(k.description || '').toLowerCase().includes(q)) return false
    return true
  })
})

function scopeVariant(s: KnowledgeScope) {
  return s === 'public' ? 'info' : s === 'org' ? 'accent' : 'success'
}

function formatTime(iso: string) {
  try {
    const d = new Date(iso)
    return d.toLocaleDateString('zh-CN', { year: '2-digit', month: '2-digit', day: '2-digit' })
  } catch {
    return '—'
  }
}
</script>

<style lang="scss" scoped>
@use '@/styles/tokens' as *;

.kb-list-page {
  &__head {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: $s-4;
    margin-bottom: $s-6;
    padding-bottom: $s-6;
    border-bottom: 1px solid $border-subtle;
  }
  &__title {
    margin-top: $s-3;
  }
  &__lede {
    margin-top: $s-3;
    color: $text-secondary;
    font-size: $fs-15;
    max-width: 480px;
  }
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: $s-4;
  margin-bottom: $s-6;

  &__search {
    display: flex;
    align-items: center;
    gap: $s-2;
    padding: 0 $s-3;
    background: $bg-surface;
    border: 1px solid $border-subtle;
    border-radius: $r-md;
    color: $text-tertiary;
    width: 280px;
    transition: border-color $dur-base $ease-out;

    &:focus-within { border-color: $accent; }
  }
  &__input {
    background: transparent;
    border: none;
    outline: none;
    height: 36px;
    flex: 1;
    color: $text-primary;
    font-size: $fs-14;
    &::placeholder { color: $text-tertiary; }
  }
  &__chips {
    display: flex;
    gap: $s-1;
  }
  &__view {
    margin-left: auto;
    display: flex;
    background: $bg-surface;
    border: 1px solid $border-subtle;
    border-radius: $r-md;
    padding: 2px;
    gap: 2px;
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
  transition: background $dur-base $ease-out, color $dur-base $ease-out;

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

.view-btn {
  width: 28px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: $r-sm;
  color: $text-tertiary;
  cursor: pointer;
  transition: background $dur-base $ease-out, color $dur-base $ease-out;

  &:hover { color: $text-primary; }
  &--active {
    background: $bg-elevated;
    color: $accent;
  }
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: $s-4;
}

.kb-card {
  position: relative;
  display: flex;
  flex-direction: column;
  background: $bg-surface;
  border: 1px solid $border-subtle;
  border-radius: $r-lg;
  padding: $s-5;
  cursor: pointer;
  overflow: hidden;
  transition: transform $dur-base $ease-out, border-color $dur-base $ease-out, background $dur-base $ease-out;

  &::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 2px;
    background: transparent;
    transition: background $dur-base $ease-out;
  }

  &:hover {
    transform: translateY(-2px);
    border-color: $border-strong;
    background: $bg-elevated;
    &::before { background: $accent; }
    .kb-card__arrow { color: $accent; transform: translateX(2px); }
  }

  &__head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: $s-3;
  }
  &__index {
    font-family: $font-mono;
    font-size: $fs-13;
    color: $accent;
    letter-spacing: 0.05em;
  }
  &__name {
    font-family: $font-display;
    font-size: $fs-20;
    font-weight: $fw-semibold;
    color: $text-primary;
    letter-spacing: -0.01em;
    line-height: 1.2;
  }
  &__desc {
    margin-top: $s-2;
    font-size: $fs-13;
    color: $text-secondary;
    line-height: $lh-snug;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    min-height: 36px;
  }
  &__meta {
    margin-top: $s-4;
    display: flex;
    align-items: center;
    gap: $s-2;
    font-size: $fs-13;
  }
  &__footer {
    margin-top: $s-4;
    padding-top: $s-4;
    border-top: 1px solid $border-subtle;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: $s-4;
  }
  &__stat {
    display: flex;
    flex-direction: column;
    gap: 2px;
    &-num {
      font-family: $font-display;
      font-size: $fs-20;
      color: $text-primary;
      font-weight: $fw-semibold;
      line-height: 1;
    }
    &-label {
      font-size: $fs-12;
      color: $text-tertiary;
    }
  }
  &__arrow {
    color: $text-tertiary;
    transition: transform $dur-base $ease-out, color $dur-base $ease-out;
  }
}

.skel-card {
  height: 200px;
  background: linear-gradient(90deg, $bg-surface 0%, $bg-elevated 50%, $bg-surface 100%);
  background-size: 200% 100%;
  border-radius: $r-lg;
  animation: shimmer 1.6s linear infinite;
  border: 1px solid $border-subtle;
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.table {
  background: $bg-surface;
  border: 1px solid $border-subtle;
  border-radius: $r-lg;
  overflow: hidden;

  &__head {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 80px 100px 40px;
    padding: $s-3 $s-4;
    background: $bg-elevated;
    border-bottom: 1px solid $border-subtle;
    font-size: $fs-12;
    font-weight: $fw-medium;
    color: $text-tertiary;
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }
  &__row {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 80px 100px 40px;
    align-items: center;
    padding: $s-3 $s-4;
    border-bottom: 1px solid $border-subtle;
    cursor: pointer;
    transition: background $dur-base $ease-out;
    &:last-child { border-bottom: none; }
    &:hover { background: $bg-elevated; }
  }
  &__cell {
    font-size: $fs-13;
    display: flex;
    align-items: center;
    gap: $s-2;
    &--main { gap: $s-3; }
    &--end { justify-content: flex-end; }
    &.num { justify-content: flex-end; font-feature-settings: "tnum"; }
  }
  &__name { color: $text-primary; font-weight: $fw-medium; }
  &__status { display: inline-flex; align-items: center; gap: $s-2; }
}

@media (max-width: 800px) {
  .filter-bar { flex-wrap: wrap; }
  .grid { grid-template-columns: 1fr; }
}
</style>