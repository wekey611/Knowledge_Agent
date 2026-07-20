<template>
  <div
    class="kb-card"
    :class="{ loading: loading, 'has-action': !loading }"
    @click="!loading && $emit('click')"
  >
    <!-- Loading skeleton -->
    <template v-if="loading">
      <div class="skeleton-color-bar" />
      <div class="skeleton-content">
        <div class="skeleton-title" />
        <div class="skeleton-desc" />
        <div class="skeleton-meta" />
      </div>
    </template>

    <!-- Normal card -->
    <template v-else>
      <div class="card-color-bar" :style="{ background: kb.color || 'var(--color-primary)' }" />
      <div class="card-content">
        <div class="card-header">
          <h3 class="card-title">{{ kb.name }}</h3>
          <el-tag size="small" type="info" class="doc-count">{{ kb.documentCount }} 文档</el-tag>
        </div>
        <p class="card-desc">{{ kb.description }}</p>
        <div class="card-footer">
          <span class="card-date">更新于 {{ formatDate(kb.updatedAt) }}</span>
          <div class="card-actions">
            <el-tooltip content="进入问答">
              <el-button
                size="small"
                type="primary"
                :icon="ChatDotSquare"
                circle
                @click.stop="$emit('chat')"
              />
            </el-tooltip>
            <el-tooltip content="浏览文档">
              <el-button
                size="small"
                :icon="Document"
                circle
                @click.stop="$emit('browse')"
              />
            </el-tooltip>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ChatDotSquare, Document } from '@element-plus/icons-vue'
import type { KnowledgeBase } from '@/types/knowledge'

defineProps<{
  kb: KnowledgeBase
  loading?: boolean
}>()

defineEmits<{
  click: []
  chat: []
  browse: []
}>()

function formatDate(dateStr: string): string {
  try {
    const date = new Date(dateStr)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))

    if (days === 0) return '今天'
    if (days === 1) return '昨天'
    if (days < 7) return `${days} 天前`
    if (days < 30) return `${Math.floor(days / 7)} 周前`
    return date.toLocaleDateString('zh-CN')
  } catch {
    return dateStr
  }
}
</script>

<style scoped>
.kb-card {
  background: var(--color-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border-light);
  overflow: hidden;
  transition: all var(--transition-normal);
}

.kb-card.has-action {
  cursor: pointer;
}

.kb-card.has-action:hover {
  box-shadow: var(--shadow-md), var(--glow-primary);
  transform: translateY(-2px);
  border-color: var(--color-primary);
}

.kb-card.has-action:hover .card-color-bar {
  background: var(--gradient-tech) !important;
  height: 4px;
}

/* Color bar */
.card-color-bar,
.skeleton-color-bar {
  height: 4px;
}

.skeleton-color-bar {
  background: var(--color-muted);
}

/* Content */
.card-content {
  padding: var(--space-6);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}

.card-title {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-foreground);
  line-height: 1.4;
}

.doc-count {
  flex-shrink: 0;
}

.card-desc {
  font-size: var(--text-sm);
  color: var(--color-muted-foreground);
  line-height: 1.6;
  margin-bottom: var(--space-5);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-date {
  font-size: var(--text-xs);
  color: var(--color-muted-foreground);
}

.card-actions {
  display: flex;
  gap: var(--space-2);
}

/* Skeleton */
.skeleton-content {
  padding: var(--space-6);
}

.skeleton-title {
  width: 60%;
  height: 18px;
  border-radius: var(--radius-sm);
  background: var(--color-muted);
  margin-bottom: var(--space-3);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.skeleton-desc {
  width: 90%;
  height: 14px;
  border-radius: var(--radius-sm);
  background: var(--color-muted);
  margin-bottom: var(--space-5);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.skeleton-meta {
  width: 40%;
  height: 12px;
  border-radius: var(--radius-sm);
  background: var(--color-muted);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

@keyframes skeleton-pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}
</style>
