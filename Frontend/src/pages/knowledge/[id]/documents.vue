<template>
  <div class="knowledge-documents">
    <EmptyState
      v-if="kbLoading"
      type="loading"
      title="加载文档..."
    />
    <EmptyState
      v-else-if="!knowledgeBase"
      type="error"
      title="知识库未找到"
      description="请返回仪表盘选择有效的知识库"
      action-label="返回仪表盘"
      @action="$router.push('/dashboard')"
    />
    <div v-else class="doc-page">
      <div class="doc-page-header">
        <h2 class="doc-page-title">{{ knowledgeBase.name }} - 文档</h2>
        <p class="doc-page-desc">共 {{ knowledgeBase.document_count }} 个文档</p>
      </div>

      <EmptyState
        v-if="!knowledgeBase"
        type="empty"
        title="暂无文档"
        description="该知识库还没有上传文档"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { KnowledgeBase } from '@/types/knowledge'
import EmptyState from '@/components/common/EmptyState.vue'

defineProps<{
  knowledgeBase: KnowledgeBase | null
  kbLoading: boolean
}>()
</script>

<style scoped>
.knowledge-documents {
  height: 100%;
  overflow-y: auto;
}

.doc-page {
  padding: var(--space-7);
}

.doc-page-header {
  margin-bottom: var(--space-8);
}

.doc-page-title {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  font-weight: 600;
  color: var(--color-foreground);
  margin-bottom: var(--space-2);
}

.doc-page-desc {
  font-size: var(--text-sm);
  color: var(--color-muted-foreground);
}
</style>
