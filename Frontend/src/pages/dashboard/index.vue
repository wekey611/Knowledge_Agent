<template>
  <div class="dashboard">
    <header class="dashboard__hero">
      <div class="dashboard__hero-text">
        <span class="eyebrow">工作台</span>
        <h1 class="display-2 dashboard__title">
          {{ greeting }}<span class="accent-text">.</span>
        </h1>
        <p class="dashboard__lede">
          {{ stats.knowledgeBases }} 个知识库 · {{ stats.documents }} 份文档 · {{ stats.chunks }} 个索引片段
        </p>
      </div>
      <div class="dashboard__hero-actions">
        <button class="btn btn--primary" @click="$router.push('/knowledge')">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14" stroke-linecap="round"/></svg>
          新建知识库
        </button>
        <button class="btn btn--ghost" @click="$router.push('/organizations')">浏览组织</button>
      </div>
    </header>

    <!-- Stat row -->
    <section class="stat-row">
      <article v-for="s in statCards" :key="s.label" class="stat-card">
        <div class="stat-card__head">
          <span class="eyebrow">{{ s.label }}</span>
          <span class="stat-card__icon" :style="{ color: s.color }" v-html="s.icon" />
        </div>
        <div class="stat-card__value mono">{{ s.value }}</div>
      </article>
    </section>

    <div class="dashboard__grid">
      <!-- Recent activity -->
      <section class="dashboard__col dashboard__col--main">
        <div class="section-head">
          <h2 class="section-head__title">最近的知识库</h2>
          <router-link to="/knowledge" class="section-head__link">查看全部 →</router-link>
        </div>

        <div v-if="loading" class="skeleton-list">
          <div v-for="i in 3" :key="i" class="skeleton-row" />
        </div>

        <div v-else-if="recent.length === 0" class="empty-card">
          <EmptyState title="还没有知识库" description="从一个知识库开始：上传文件、构建索引、向它提问。">
            <template #action>
              <button class="btn btn--primary" @click="$router.push('/knowledge')">创建第一个知识库</button>
            </template>
          </EmptyState>
        </div>

        <ul v-else class="recent-list">
          <li
            v-for="kb in recent"
            :key="kb.id"
            class="recent-row"
            @click="$router.push(`/knowledge/${kb.id}`)"
          >
            <div class="recent-row__main">
              <span class="status-dot" :class="`status-dot--${statusClass(kb.status)}`" />
              <div class="recent-row__text">
                <span class="recent-row__name">{{ kb.name }}</span>
                <span class="recent-row__desc">{{ kb.description || '无描述' }}</span>
              </div>
            </div>
            <div class="recent-row__stats mono">
              <span><strong>{{ kb.document_count }}</strong> 文档</span>
              <span class="faint">·</span>
              <span class="muted">{{ kb.scope === 'public' ? '公开' : kb.scope === 'org' ? '组织' : '个人' }}</span>
            </div>
            <div class="recent-row__time faint mono">{{ formatTime(kb.created_at) }}</div>
          </li>
        </ul>
      </section>

      <!-- Quick actions + shortcuts -->
      <aside class="dashboard__col dashboard__col--side">
        <div class="section-head">
          <h2 class="section-head__title">快捷操作</h2>
        </div>
        <div class="quick-grid">
          <button class="quick-card" @click="$router.push('/knowledge')">
            <span class="quick-card__icon accent-text">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 5a2 2 0 0 1 2-2h3l2 2h7a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2z"/></svg>
            </span>
            <span class="quick-card__label">新建知识库</span>
            <span class="quick-card__hint">上传文档 · 构建索引</span>
          </button>
          <button class="quick-card" @click="$router.push('/organizations')">
            <span class="quick-card__icon">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="9" cy="8" r="3"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><circle cx="17" cy="6" r="2.5"/></svg>
            </span>
            <span class="quick-card__label">加入组织</span>
            <span class="quick-card__hint">协作 · 共享知识库</span>
          </button>
          <button class="quick-card" @click="$router.push('/knowledge')">
            <span class="quick-card__icon">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 5a2 2 0 0 1 2-2h3l2 2h7a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2z"/><path d="M8 9h8M8 13h6" stroke-linecap="round"/></svg>
            </span>
            <span class="quick-card__label">浏览知识库</span>
            <span class="quick-card__hint">查看所有 KB</span>
          </button>
        </div>

        <div class="hint-card">
          <span class="eyebrow">新手上路</span>
          <p>
            第一次使用？先到
            <router-link to="/knowledge" class="hint-card__link">公共知识库</router-link>
            翻翻示例文档，里面有完整的使用说明。
          </p>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { fetchKnowledgeBases } from '@/api/knowledge'
import { fetchOrganizations } from '@/api/organization'
import EmptyState from '@/components/common/EmptyState.vue'
import type { KnowledgeBaseSimple, KBStatus } from '@/types/knowledge'

const recent = ref<KnowledgeBaseSimple[]>([])
const loading = ref(true)
const orgCount = ref(0)

onMounted(async () => {
  try {
    const [kbs, orgs] = await Promise.allSettled([
      fetchKnowledgeBases(),
      fetchOrganizations(),
    ])
    if (kbs.status === 'fulfilled') recent.value = kbs.value.data
    if (orgs.status === 'fulfilled') orgCount.value = orgs.value.length
  } finally {
    loading.value = false
  }
})

const stats = computed(() => {
  const docs = recent.value.reduce((sum, k) => sum + k.document_count, 0)
  return {
    knowledgeBases: recent.value.length,
    documents: docs,
    chunks: docs * 47, // mock 估算；后端接入后用真实数据
    organizations: orgCount.value,
  }
})

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '深夜好'
  if (h < 12) return '早上好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
})

const statCards = computed(() => [
  {
    label: '知识库',
    value: stats.value.knowledgeBases,
    delta: '+0',
    deltaUnit: '本周',
    deltaClass: 'delta--neutral',
    icon: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 5a2 2 0 0 1 2-2h3l2 2h7a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2z"/></svg>',
    color: '#A8E6CF',
  },
  {
    label: '文档',
    value: stats.value.documents,
    delta: '+0',
    deltaUnit: '本周',
    deltaClass: 'delta--neutral',
    icon: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6"/></svg>',
    color: '#6B9DD9',
  },
  {
    label: '索引片段',
    value: stats.value.chunks,
    delta: '—',
    deltaUnit: '估算',
    deltaClass: 'delta--neutral',
    icon: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M3 15h18M9 3v18M15 3v18"/></svg>',
    color: '#F5A623',
  },
  {
    label: '组织',
    value: stats.value.organizations,
    delta: '—',
    deltaUnit: '—',
    deltaClass: 'delta--neutral',
    icon: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="9" cy="8" r="3"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/></svg>',
    color: '#E5484D',
  },
])

function statusClass(s: KBStatus) {
  if (s === 'active') return 'active'
  if (s === 'provisioning') return 'provision'
  if (s === 'failed') return 'failed'
  return 'archived'
}

function formatTime(iso: string) {
  try {
    const d = new Date(iso)
    const diff = Date.now() - d.getTime()
    const days = Math.floor(diff / 86400000)
    if (days < 1) return '今天'
    if (days < 7) return `${days} 天前`
    return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
  } catch {
    return ''
  }
}
</script>

<style lang="scss" scoped>
@use '@/styles/tokens' as *;

.dashboard {
  &__hero {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: $s-6;
    margin-bottom: $s-8;
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
  }
  &__hero-actions {
    display: flex;
    gap: $s-2;
  }

  &__grid {
    display: grid;
    grid-template-columns: 1.4fr 1fr;
    gap: $s-8;
    margin-top: $s-8;
  }
}

.stat-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: $s-4;
}

.stat-card {
  background: $bg-surface;
  border: 1px solid $border-subtle;
  border-radius: $r-lg;
  padding: $s-5;
  display: flex;
  flex-direction: column;
  gap: $s-3;
  transition: border-color $dur-base $ease-out, transform $dur-base $ease-out;
  &:hover { border-color: $border-strong; }

  &__head {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  &__icon {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: $r-md;
    background: $bg-elevated;
  }
  &__value {
    font-family: $font-display;
    font-size: $fs-32;
    font-weight: $fw-semibold;
    line-height: 1;
    letter-spacing: -0.02em;
  }
  &__delta {
    font-size: $fs-13;
    display: flex;
    align-items: baseline;
    gap: $s-1;
  }
}

.delta--neutral { color: $text-secondary; }

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: $s-4;

  &__title {
    font-family: $font-body;
    font-weight: $fw-semibold;
    font-size: $fs-15;
    color: $text-primary;
  }
  &__link {
    font-size: $fs-13;
    color: $accent;
    text-decoration: none;
    &:hover { color: $accent-hover; }
  }
}

.recent-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: $s-2;
}

.recent-row {
  display: flex;
  align-items: center;
  gap: $s-4;
  padding: $s-4 $s-4;
  background: $bg-surface;
  border: 1px solid $border-subtle;
  border-radius: $r-md;
  cursor: pointer;
  transition: background $dur-base $ease-out, border-color $dur-base $ease-out, transform $dur-base $ease-out;

  &:hover {
    background: $bg-elevated;
    border-color: $border-strong;
    transform: translateX(2px);
  }

  &__main {
    display: flex;
    align-items: center;
    gap: $s-3;
    flex: 1;
    min-width: 0;
  }
  &__text {
    display: flex;
    flex-direction: column;
    min-width: 0;
  }
  &__name {
    font-size: $fs-14;
    font-weight: $fw-medium;
    color: $text-primary;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  &__desc {
    font-size: $fs-12;
    color: $text-tertiary;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  &__stats {
    font-size: $fs-13;
    color: $text-secondary;
    display: flex;
    align-items: center;
    gap: $s-2;
    strong { color: $text-primary; font-weight: $fw-semibold; }
  }
  &__time {
    font-size: $fs-12;
    min-width: 60px;
    text-align: right;
  }
}

.empty-card {
  background: $bg-surface;
  border: 1px dashed $border-strong;
  border-radius: $r-lg;
}

.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: $s-2;
}
.skeleton-row {
  height: 64px;
  background: linear-gradient(90deg, $bg-surface 0%, $bg-elevated 50%, $bg-surface 100%);
  background-size: 200% 100%;
  border-radius: $r-md;
  animation: shimmer 1.6s linear infinite;
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.quick-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: $s-3;
  margin-bottom: $s-5;
}

.quick-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: $s-2;
  padding: $s-4;
  background: $bg-surface;
  border: 1px solid $border-subtle;
  border-radius: $r-md;
  cursor: pointer;
  text-align: left;
  transition: all $dur-base $ease-out;

  &:hover {
    border-color: $border-strong;
    background: $bg-elevated;
    transform: translateY(-1px);
  }

  &__icon {
    width: 36px;
    height: 36px;
    border-radius: $r-sm;
    background: $bg-elevated;
    display: flex;
    align-items: center;
    justify-content: center;
    color: $text-secondary;
  }
  &__label {
    font-size: $fs-14;
    font-weight: $fw-medium;
    color: $text-primary;
  }
  &__hint {
    font-size: $fs-12;
    color: $text-tertiary;
  }
  &--accent {
    background: linear-gradient(135deg, $bg-surface 0%, $accent-soft 200%);
    .quick-card__icon { background: rgba(168, 230, 207, 0.15); }
  }
}

.hint-card {
  padding: $s-4;
  background: $bg-surface;
  border: 1px dashed $border-subtle;
  border-radius: $r-md;

  .eyebrow { display: block; margin-bottom: $s-2; }
  p {
    font-size: $fs-13;
    color: $text-secondary;
    line-height: $lh-snug;
  }
  &__link {
    color: $accent;
    text-decoration: none;
    font-weight: $fw-medium;
    &:hover { color: $accent-hover; text-decoration: underline; }
  }
}

@media (max-width: 960px) {
  .stat-row { grid-template-columns: repeat(2, 1fr); }
  .dashboard__grid { grid-template-columns: 1fr; }
  .dashboard__hero { flex-direction: column; align-items: flex-start; }
}
</style>