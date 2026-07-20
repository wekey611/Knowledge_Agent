<template>
  <div class="kb-grid-wrapper">
    <!-- Loading: skeleton cards -->
    <div v-if="loading" class="kb-grid">
      <KnowledgeBaseCard
        v-for="i in 6"
        :key="`skeleton-${i}`"
        :kb="{ id: i, name: '', description: '', documentCount: 0, createdAt: '', updatedAt: '' }"
        loading
      />
    </div>

    <!-- Error state -->
    <EmptyState
      v-else-if="error"
      type="error"
      title="加载失败"
      :description="error"
      action-label="重试"
      @action="$emit('retry')"
    />

    <!-- Empty state -->
    <EmptyState
      v-else-if="knowledgeBases.length === 0"
      type="empty"
      title="暂无知识库"
      description="你还没有创建任何知识库。创建你的第一个知识库，开始管理和探索知识吧！"
    />

    <!-- Grid of KB cards -->
    <div v-else class="kb-grid">
      <KnowledgeBaseCard
        v-for="kb in knowledgeBases"
        :key="kb.id"
        :kb="kb"
        @click="$emit('select', kb.id)"
        @chat="$emit('chat', kb.id)"
        @browse="$emit('browse', kb.id)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { KnowledgeBase } from '@/types/knowledge'
import KnowledgeBaseCard from './KnowledgeBaseCard.vue'
import EmptyState from '@/components/common/EmptyState.vue'

defineProps<{
  knowledgeBases: KnowledgeBase[]
  loading: boolean
  error: string | null
}>()

defineEmits<{
  select: [id: number]
  chat: [id: number]
  browse: [id: number]
  retry: []
}>()
</script>

<style scoped>
.kb-grid-wrapper {
  width: 100%;
}

.kb-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--space-6);
}
</style>
