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
      <div class="card-color-bar" :style="{ background: cardColor }" />
      <div class="card-content">
        <div class="card-header">
          <h3 class="card-title">{{ kb.name }}</h3>
          <el-tag size="small" type="info" class="doc-count">{{ kb.document_count }} 文档</el-tag>
        </div>

        <div class="card-badges">
          <el-tag size="small" :color="scopeTagColor" class="scope-tag" effect="dark">
            {{ SCOPE_LABELS[kb.scope] }}
          </el-tag>
          <el-tag
            v-if="kb.status !== 'active'"
            size="small"
            :type="kb.status === 'failed' ? 'danger' : 'warning'"
          >
            {{ KB_STATUS_LABELS[kb.status] }}
          </el-tag>
        </div>

        <p class="card-desc">{{ kb.description || '暂无描述' }}</p>
        <div class="card-footer">
          <span class="card-date">创建于 {{ formatDate(kb.created_at) }}</span>
          <div class="card-actions" @click.stop>
            <el-tooltip content="编辑">
              <el-button
                size="small"
                :icon="Edit"
                circle
                @click="$emit('edit')"
              />
            </el-tooltip>
            <el-tooltip content="删除">
              <el-button
                size="small"
                type="danger"
                :icon="Delete"
                circle
                @click="$emit('delete')"
              />
            </el-tooltip>
            <el-tooltip content="进入问答">
              <el-button
                size="small"
                type="primary"
                :icon="ChatDotSquare"
                circle
                @click="$emit('chat')"
              />
            </el-tooltip>
            <el-tooltip content="浏览文档">
              <el-button
                size="small"
                :icon="Document"
                circle
                @click="$emit('browse')"
              />
            </el-tooltip>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ChatDotSquare, Delete, Document, Edit } from '@element-plus/icons-vue'
import {
  KB_STATUS_LABELS,
  SCOPE_COLORS,
  SCOPE_LABELS,
  type KnowledgeBaseSimple,
} from '@/types/knowledge'

const props = defineProps<{
  kb: KnowledgeBaseSimple
  loading?: boolean
}>()

defineEmits<{
  click: []
  edit: []
  delete: []
  chat: []
  browse: []
}>()

const cardColor = computed(() => SCOPE_COLORS[props.kb.scope])

const scopeTagColor = computed(() => SCOPE_COLORS[props.kb.scope])

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

.card-badges {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
}

.scope-tag {
  border: none;
  font-weight: 500;
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
  min-height: calc(1.6em * 2);
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-3);
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
