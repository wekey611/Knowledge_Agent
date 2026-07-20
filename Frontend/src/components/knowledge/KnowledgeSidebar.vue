<template>
  <aside class="knowledge-sidebar">
    <!-- KB header -->
    <div class="ks-header">
      <button class="back-btn" @click="$router.push('/dashboard')">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="19" y1="12" x2="5" y2="12" />
          <polyline points="12 19 5 12 12 5" />
        </svg>
      </button>
      <div class="ks-title-group">
        <h3 class="ks-title">{{ knowledgeBase?.name || '知识库' }}</h3>
        <span v-if="knowledgeBase" class="ks-doc-count">{{ knowledgeBase.documentCount }} 文档</span>
      </div>
    </div>

    <!-- Search within KB -->
    <div class="ks-search">
      <input
        v-model="searchQuery"
        type="text"
        class="ks-search-input"
        placeholder="搜索文档..."
      />
    </div>

    <!-- Document tree -->
    <div class="ks-content">
      <!-- Loading skeleton -->
      <div v-if="loading" class="ks-loading">
        <div v-for="i in 5" :key="i" class="skeleton-row" />
      </div>

      <!-- Empty state -->
      <EmptyState
        v-else-if="documents.length === 0"
        type="empty"
        title="暂无文档"
        description="该知识库还没有上传文档"
      />

      <!-- Document tree -->
      <div v-else class="doc-tree">
        <div
          v-for="doc in filteredDocuments"
          :key="doc.id"
          class="doc-item"
          :class="{ active: activeDocId === doc.id }"
          @click="$emit('select-doc', doc.id)"
        >
          <div class="doc-icon">
            <svg v-if="doc.fileType === 'pdf'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
            </svg>
            <svg v-else-if="doc.fileType === 'md'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
            </svg>
            <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
            </svg>
          </div>
          <span class="doc-name">{{ doc.title }}</span>
          <span class="doc-type">{{ doc.fileType.toUpperCase() }}</span>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { KnowledgeBase, Document } from '@/types/knowledge'
import EmptyState from '@/components/common/EmptyState.vue'

const props = defineProps<{
  knowledgeBase: KnowledgeBase | null
  documents: Document[]
  loading: boolean
  activeDocId?: number | null
}>()

defineEmits<{
  'select-doc': [id: number]
}>()

const searchQuery = ref('')

const filteredDocuments = computed(() => {
  if (!searchQuery.value.trim()) return props.documents
  const q = searchQuery.value.toLowerCase()
  return props.documents.filter((d) => d.title.toLowerCase().includes(q))
})
</script>

<style scoped>
.knowledge-sidebar {
  width: 280px;
  min-width: 280px;
  background: var(--color-card);
  border-right: 1px solid var(--color-border-light);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  flex-shrink: 0;
}

/* Header */
.ks-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-5);
  border-bottom: 1px solid var(--color-border-light);
}

.back-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  border: none;
  background: transparent;
  color: var(--color-muted-foreground);
  cursor: pointer;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.back-btn:hover {
  background: var(--color-muted);
  color: var(--color-foreground);
}

.ks-title-group {
  min-width: 0;
  flex: 1;
}

.ks-title {
  font-family: var(--font-heading);
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-foreground);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ks-doc-count {
  font-size: var(--text-xs);
  color: var(--color-muted-foreground);
}

/* Search */
.ks-search {
  padding: var(--space-3) var(--space-5);
}

.ks-search-input {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-light);
  background: var(--color-bg);
  font-size: var(--text-xs);
  color: var(--color-foreground);
  outline: none;
  transition: all var(--transition-fast);
}

.ks-search-input:focus {
  border-color: var(--color-primary);
  box-shadow: var(--focus-ring);
}

.ks-search-input::placeholder {
  color: var(--color-muted-foreground);
}

/* Content */
.ks-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-2);
}

/* Loading skeleton */
.ks-loading {
  padding: var(--space-3);
}

.skeleton-row {
  height: 16px;
  border-radius: var(--radius-sm);
  background: var(--color-muted);
  margin-bottom: var(--space-3);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.skeleton-row:nth-child(even) {
  width: 80%;
}

/* Document tree */
.doc-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.doc-item:hover {
  background: var(--color-muted);
}

.doc-item.active {
  background: var(--color-primary-bg);
  color: var(--color-primary);
}

.doc-icon {
  display: flex;
  align-items: center;
  flex-shrink: 0;
  color: var(--color-muted-foreground);
}

.doc-item.active .doc-icon {
  color: var(--color-primary);
}

.doc-name {
  flex: 1;
  font-size: var(--text-xs);
  color: var(--color-foreground);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.doc-type {
  font-size: 10px;
  font-weight: 600;
  color: var(--color-muted-foreground);
  letter-spacing: 0.05em;
  flex-shrink: 0;
}

@keyframes skeleton-pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}
</style>
