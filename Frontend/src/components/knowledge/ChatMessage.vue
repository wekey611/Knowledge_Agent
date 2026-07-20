<template>
  <div class="chat-message" :class="`role-${message.role}`">
    <!-- AI avatar -->
    <div v-if="message.role === 'assistant'" class="msg-avatar">
      <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect width="28" height="28" rx="8" fill="url(#msg-gradient)" />
        <path d="M14 6C9.58 6 6 9.58 6 14s3.58 8 8 8 8-3.58 8-8-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6s2.69-6 6-6 6 2.69 6 6-2.69 6-6 6z" fill="white" opacity="0.9" />
        <path d="M14 9c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-2.21 0-4 1.79-4 4h8c0-2.21-1.79-4-4-4z" fill="white" />
        <defs>
          <linearGradient id="msg-gradient" x1="0" y1="0" x2="28" y2="28" gradientUnits="userSpaceOnUse">
            <stop class="msg-grad-start" />
            <stop class="msg-grad-end" offset="1" />
          </linearGradient>
        </defs>
      </svg>
    </div>

    <!-- Message bubble -->
    <div class="msg-bubble" :class="{ streaming: streaming, error: message.status === 'error' }">
      <div class="msg-content" v-html="renderedContent" />

      <!-- Sources -->
      <div v-if="message.sources && message.sources.length > 0" class="msg-sources">
        <div class="sources-label">来源</div>
        <div class="sources-list">
          <el-tag
            v-for="source in message.sources"
            :key="source.documentId"
            size="small"
            type="info"
            class="source-tag"
          >
            {{ source.documentTitle }}
          </el-tag>
        </div>
      </div>

      <!-- Error state -->
      <div v-if="message.status === 'error'" class="msg-error">
        <span>发送失败</span>
        <button class="retry-btn" @click="$emit('retry')">重试</button>
      </div>
    </div>

    <!-- User avatar placeholder -->
    <div v-if="message.role === 'user'" class="msg-avatar user-avatar">
      <span>{{ userInitial }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ChatMessage } from '@/types/knowledge'

const props = defineProps<{
  message: ChatMessage
  streaming?: boolean
  userInitial?: string
}>()

defineEmits<{
  retry: []
}>()

// Render markdown-like content to HTML (simple formatting)
const renderedContent = computed(() => {
  let text = props.message.content

  // Escape HTML
  text = text.replace(/</g, '&lt;').replace(/>/g, '&gt;')

  // Convert markdown bold
  text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')

  // Convert newlines to paragraphs
  const lines = text.split('\n')
  let html = ''
  let inList = false

  lines.forEach((line) => {
    if (line.startsWith('- ') || line.startsWith('* ')) {
      if (!inList) {
        html += '<ul>'
        inList = true
      }
      html += `<li>${line.slice(2)}</li>`
    } else {
      if (inList) {
        html += '</ul>'
        inList = false
      }
      if (line.trim() === '') {
        html += '<br>'
      } else if (/^\d+\.\s/.test(line)) {
        const match = line.match(/^\d+\.\s(.+)/)
        html += match ? `<p class="numbered">${match[1]}</p>` : `<p>${line}</p>`
      } else {
        html += `<p>${line}</p>`
      }
    }
  })

  if (inList) html += '</ul>'

  return html
})
</script>

<style scoped>
.chat-message {
  display: flex;
  gap: var(--space-3);
  margin-bottom: var(--space-6);
  align-items: flex-start;
  max-width: 800px;
}

.chat-message.role-user {
  flex-direction: row-reverse;
  margin-left: auto;
}

.msg-avatar {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-avatar {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-full);
  background: var(--color-primary);
  color: white;
  font-size: var(--text-xs);
  font-weight: 600;
}

.msg-bubble {
  max-width: 75%;
  padding: var(--space-4) var(--space-5);
  border-radius: var(--radius-lg);
  line-height: 1.6;
  font-size: var(--text-sm);
}

.role-assistant .msg-bubble {
  background: var(--color-card);
  border: 1px solid var(--color-border-light);
  color: var(--color-foreground);
  border-bottom-left-radius: var(--space-2);
}

.role-user .msg-bubble {
  background: var(--color-primary);
  color: white;
  border-bottom-right-radius: var(--space-2);
}

.msg-bubble.streaming {
  border-left: 3px solid var(--color-accent);
}

.msg-bubble.error {
  border: 1px solid var(--color-error);
  opacity: 0.8;
}

/* Message content styles */
.msg-content :deep(p) {
  margin-bottom: var(--space-2);
}

.msg-content :deep(p:last-child) {
  margin-bottom: 0;
}

.msg-content :deep(ul) {
  list-style: disc;
  padding-left: var(--space-6);
  margin-bottom: var(--space-2);
}

.msg-content :deep(li) {
  margin-bottom: var(--space-1);
}

.msg-content :dup(strong) {
  font-weight: 600;
}

.role-user .msg-content :deep(strong) {
  color: inherit;
}

/* Sources */
.msg-sources {
  margin-top: var(--space-4);
  padding-top: var(--space-3);
  border-top: 1px solid var(--color-border-light);
}

.sources-label {
  font-size: var(--text-xs);
  color: var(--color-muted-foreground);
  font-weight: 600;
  margin-bottom: var(--space-2);
}

.sources-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.source-tag {
  cursor: pointer;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Error state */
.msg-error {
  margin-top: var(--space-3);
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-size: var(--text-xs);
  color: var(--color-error);
}

.retry-btn {
  background: none;
  border: 1px solid var(--color-error);
  color: var(--color-error);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.retry-btn:hover {
  background: var(--color-error);
  color: white;
}

/* SVG gradient — controlled via CSS variables */
.msg-grad-start { stop-color: var(--color-primary); }
.msg-grad-end { stop-color: var(--color-accent); }
</style>
