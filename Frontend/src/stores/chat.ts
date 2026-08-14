// ========================================
// Chat Store — Message State Management
// ========================================
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ChatMessage } from '@/types/knowledge'
import { fetchMessages, sendMessage } from '@/api/chatMock'

export const useChatStore = defineStore('chat', () => {
  const messagesByKb = ref<Record<number, ChatMessage[]>>({})
  const loading = ref(false)
  const sending = ref(false)
  const error = ref<string | null>(null)

  function getMessages(kbId: number): ChatMessage[] {
    return messagesByKb.value[kbId] || []
  }

  async function loadMessages(kbId: number) {
    loading.value = true
    error.value = null
    try {
      const messages = await fetchMessages(kbId)
      messagesByKb.value[kbId] = messages
    } catch (e: any) {
      error.value = e?.message || '加载消息失败'
    } finally {
      loading.value = false
    }
  }

  async function send(kbId: number, content: string): Promise<boolean> {
    if (!content.trim() || sending.value) return false

    sending.value = true

    // Optimistic add user message
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      knowledgeBaseId: kbId,
      role: 'user',
      content: content.trim(),
      createdAt: new Date().toISOString(),
      status: 'sent',
    }

    if (!messagesByKb.value[kbId]) {
      messagesByKb.value[kbId] = []
    }
    messagesByKb.value[kbId].push(userMessage)

    try {
      const response = await sendMessage(kbId, content.trim())
      messagesByKb.value[kbId].push(response)
      return true
    } catch (e: any) {
      // Mark user message as error
      userMessage.status = 'error'
      error.value = e?.message || '发送失败'
      return false
    } finally {
      sending.value = false
    }
  }

  function clearMessages(kbId: number) {
    messagesByKb.value[kbId] = []
  }

  return {
    loading,
    sending,
    error,
    getMessages,
    loadMessages,
    send,
    clearMessages,
  }
})
