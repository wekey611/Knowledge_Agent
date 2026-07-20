<template>
  <div class="knowledge-chat">
    <!-- Loading -->
    <EmptyState
      v-if="kbLoading"
      type="loading"
      title="加载知识库..."
    />

    <!-- Not found -->
    <EmptyState
      v-else-if="!knowledgeBase"
      type="error"
      title="知识库未找到"
      description="请返回仪表盘选择有效的知识库"
      action-label="返回仪表盘"
      @action="$router.push('/dashboard')"
    />

    <!-- Chat interface -->
    <template v-else>
      <!-- Header -->
      <div class="chat-header">
        <div class="chat-header-left">
          <h2 class="chat-kb-name">{{ knowledgeBase.name }}</h2>
          <el-tag size="small" type="info" class="chat-kb-badge">
            {{ knowledgeBase.documentCount }} 文档
          </el-tag>
        </div>
        <el-button
          v-if="messages.length > 0"
          size="small"
          text
          type="danger"
          @click="handleClear"
        >
          清除对话
        </el-button>
      </div>

      <!-- Messages -->
      <ChatMessageList
        :messages="messages"
        :loading="messagesLoading"
        :sending="sending"
        :error="error"
        :user-initial="userInitial"
        @load="handleLoadMessages"
        @retry="handleRetry"
        @suggest="handleSend"
      />

      <!-- Input -->
      <ChatInput
        :disabled="false"
        :sending="sending"
        @send="handleSend"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import type { ChatMessage, KnowledgeBase } from '@/types/knowledge'
import { useAuthStore } from '@/stores/auth'
import ChatMessageList from '@/components/knowledge/ChatMessageList.vue'
import ChatInput from '@/components/knowledge/ChatInput.vue'
import EmptyState from '@/components/common/EmptyState.vue'

defineProps<{
  knowledgeBase: KnowledgeBase | null
  kbLoading: boolean
  messages: ChatMessage[]
  messagesLoading: boolean
  sending: boolean
  error: string | null
}>()

const emit = defineEmits<{
  send: [content: string]
  loadMessages: []
  retryMessage: [msg: ChatMessage]
  suggest: [question: string]
}>()

const authStore = useAuthStore()
const userInitial = computed(() => {
  return authStore.user?.email?.charAt(0).toUpperCase() || 'U'
})

function handleSend(content: string) {
  emit('send', content)
}

function handleLoadMessages() {
  emit('loadMessages')
}

function handleRetry(msg: ChatMessage) {
  emit('retryMessage', msg)
}

function handleClear() {
  // The clear is handled by the parent KnowledgeLayout
  // For now, we reload which effectively clears via re-fetch
  ElMessage.info('清除对话功能将在后续版本完善')
}
</script>

<style scoped>
.knowledge-chat {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-5) var(--space-7);
  border-bottom: 1px solid var(--color-border-light);
  background: var(--color-card);
  flex-shrink: 0;
}

.chat-header-left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.chat-kb-name {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-foreground);
}

.chat-kb-badge {
  font-weight: 500;
}
</style>
