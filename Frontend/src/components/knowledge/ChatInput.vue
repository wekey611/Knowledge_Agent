<template>
  <div class="chat-input-wrapper">
    <div class="chat-input-container" :class="{ focused: isFocused }">
      <textarea
        ref="textareaRef"
        v-model="inputText"
        class="chat-textarea"
        :placeholder="disabled ? '请选择一个知识库' : '输入你的问题...'"
        :disabled="disabled || sending"
        rows="1"
        @input="autoResize"
        @focus="isFocused = true"
        @blur="isFocused = false"
        @keydown.enter.exact.prevent="handleSend"
      />
      <button
        class="send-btn"
        :class="{ active: canSend }"
        :disabled="!canSend"
        :title="'发送'"
        @click="handleSend"
      >
        <!-- Send arrow icon -->
        <svg v-if="!sending" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="22" y1="2" x2="11" y2="13" />
          <polygon points="22 2 15 22 11 13 2 9 22 2" />
        </svg>
        <el-icon v-else class="is-loading"><Loading /></el-icon>
      </button>
    </div>
    <p v-if="sending" class="sending-hint">AI 正在生成回答...</p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Loading } from '@element-plus/icons-vue'

const props = defineProps<{
  disabled?: boolean
  sending?: boolean
}>()

const emit = defineEmits<{
  send: [content: string]
}>()

const textareaRef = ref<HTMLTextAreaElement | null>(null)
const inputText = ref('')
const isFocused = ref(false)

const canSend = computed(() => {
  return inputText.value.trim().length > 0 && !props.disabled && !props.sending
})

function autoResize() {
  const textarea = textareaRef.value
  if (!textarea) return
  textarea.style.height = 'auto'
  textarea.style.height = `${Math.min(textarea.scrollHeight, 160)}px`
}

function handleSend() {
  if (!canSend.value) return
  emit('send', inputText.value.trim())
  inputText.value = ''

  // Reset height
  const textarea = textareaRef.value
  if (textarea) {
    textarea.style.height = 'auto'
  }
}
</script>

<style scoped>
.chat-input-wrapper {
  padding: var(--space-5) var(--space-7) var(--space-6);
  border-top: 1px solid var(--color-border-light);
  background: var(--color-card);
}

.chat-input-container {
  display: flex;
  align-items: flex-end;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  background: var(--color-bg);
  transition: all var(--transition-fast);
}

.chat-input-container.focused {
  border-color: var(--color-primary);
  box-shadow: var(--focus-ring);
}

.chat-textarea {
  flex: 1;
  border: none;
  outline: none;
  resize: none;
  background: transparent;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--color-foreground);
  line-height: 1.6;
  max-height: 160px;
  min-height: 22px;
}

.chat-textarea::placeholder {
  color: var(--color-muted-foreground);
}

.chat-textarea:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.send-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  border: none;
  background: var(--color-muted);
  color: var(--color-muted-foreground);
  cursor: pointer;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.send-btn.active {
  background: var(--color-primary);
  color: white;
}

.send-btn.active:hover {
  background: var(--color-primary-hover);
}

.send-btn:disabled {
  cursor: not-allowed;
}

.sending-hint {
  font-size: var(--text-xs);
  color: var(--color-accent);
  margin-top: var(--space-2);
  text-align: right;
}
</style>
