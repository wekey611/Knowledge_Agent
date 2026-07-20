<template>
  <div class="chat-message-list" ref="listRef">
    <!-- Loading state -->
    <EmptyState
      v-if="loading"
      type="loading"
      title="加载消息中..."
    />

    <!-- Error state -->
    <EmptyState
      v-else-if="error"
      type="error"
      title="加载失败"
      :description="error"
      action-label="重试"
      @action="$emit('load')"
    />

    <!-- Empty state (first message prompt) -->
    <div v-else-if="messages.length === 0" class="empty-chat">
      <div class="empty-icon">
        <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
      </div>
      <h3 class="empty-title">开始提问</h3>
      <p class="empty-desc">你可以向知识库提问任何问题，AI 将基于知识库内容为你解答</p>
      <div class="suggested-questions">
        <button
          v-for="q in suggestedQuestions"
          :key="q"
          class="suggestion-chip"
          @click="$emit('suggest', q)"
        >
          {{ q }}
        </button>
      </div>
    </div>

    <!-- Messages -->
    <template v-else>
      <div class="messages-container">
        <ChatMessage
          v-for="msg in messages"
          :key="msg.id"
          :message="msg"
          :streaming="msg === messages[messages.length - 1] && sending"
          :user-initial="userInitial"
          @retry="$emit('retry', msg)"
        />
      </div>

      <!-- Scroll anchor -->
      <div ref="scrollAnchor" />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import type { ChatMessage as ChatMessageType } from '@/types/knowledge'
import ChatMessage from './ChatMessage.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const props = defineProps<{
  messages: ChatMessageType[]
  loading: boolean
  sending: boolean
  error: string | null
  userInitial?: string
}>()

defineEmits<{
  load: []
  retry: [msg: ChatMessageType]
  suggest: [question: string]
}>()

const listRef = ref<HTMLElement | null>(null)
const scrollAnchor = ref<HTMLElement | null>(null)

const suggestedQuestions = [
  '这个知识库包含哪些内容？',
  '帮我总结一下主要文档',
  '有哪些核心概念？',
]

// Auto scroll to bottom on new messages
watch(
  () => props.messages.length,
  async () => {
    await nextTick()
    scrollAnchor.value?.scrollIntoView({ behavior: 'smooth' })
  }
)
</script>

<style scoped>
.chat-message-list {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-7);
}

/* Empty chat state */
.empty-chat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: var(--space-10) var(--space-7);
  text-align: center;
}

.empty-icon {
  color: var(--color-muted-foreground);
  opacity: 0.3;
  margin-bottom: var(--space-6);
}

.empty-title {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  font-weight: 600;
  color: var(--color-foreground);
  margin-bottom: var(--space-3);
}

.empty-desc {
  font-size: var(--text-sm);
  color: var(--color-muted-foreground);
  max-width: 360px;
  line-height: 1.6;
  margin-bottom: var(--space-8);
}

.suggested-questions {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  width: 100%;
  max-width: 400px;
}

.suggestion-chip {
  padding: var(--space-3) var(--space-5);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-card);
  color: var(--color-foreground);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  text-align: left;
}

.suggestion-chip:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: var(--color-primary-bg);
}

/* Messages container */
.messages-container {
  padding-bottom: var(--space-7);
}
</style>
