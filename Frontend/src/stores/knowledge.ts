// ========================================
// Knowledge Store — KB State Management
// ========================================
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { KnowledgeBase } from '@/types/knowledge'
import { fetchKnowledgeBases } from '@/api/knowledge'

export const useKnowledgeStore = defineStore('knowledge', () => {
  const knowledgeBases = ref<KnowledgeBase[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const kbCount = computed(() => knowledgeBases.value.length)

  async function loadKnowledgeBases() {
    loading.value = true
    error.value = null
    try {
      knowledgeBases.value = await fetchKnowledgeBases()
    } catch (e: any) {
      error.value = e?.message || '加载知识库失败'
    } finally {
      loading.value = false
    }
  }

  function getKnowledgeBase(id: number): KnowledgeBase | undefined {
    return knowledgeBases.value.find((kb) => kb.id === id)
  }

  return {
    knowledgeBases,
    loading,
    error,
    kbCount,
    loadKnowledgeBases,
    getKnowledgeBase,
  }
})
