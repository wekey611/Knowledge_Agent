// ========================================
// Knowledge Store — KB State Management
// ========================================
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  KnowledgeBaseCreate,
  KnowledgeBaseSimple,
  KnowledgeBaseUpdate,
} from '@/types/knowledge'
import {
  createKnowledgeBase,
  deleteKnowledgeBase,
  fetchKnowledgeBase,
  fetchKnowledgeBases,
  updateKnowledgeBase,
} from '@/api/knowledge'

export const useKnowledgeStore = defineStore('knowledge', () => {
  const knowledgeBases = ref<KnowledgeBaseSimple[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const kbCount = computed(() => knowledgeBases.value.length)

  async function loadKnowledgeBases() {
    loading.value = true
    error.value = null
    try {
      const res = await fetchKnowledgeBases()
      knowledgeBases.value = res.data
    } catch (e: any) {
      error.value = e?.message || '加载知识库失败'
    } finally {
      loading.value = false
    }
  }

  function getKnowledgeBase(id: number): KnowledgeBaseSimple | undefined {
    return knowledgeBases.value.find((kb) => kb.id === id)
  }

  /** 拉取详情（刷新单个 KB 的最新状态，如 status/document_count） */
  async function refreshKnowledgeBase(id: number) {
    try {
      const detail = await fetchKnowledgeBase(id)
      const idx = knowledgeBases.value.findIndex((kb) => kb.id === id)
      if (idx !== -1) {
        knowledgeBases.value[idx] = { ...knowledgeBases.value[idx], ...detail }
      }
      return detail
    } catch {
      return null
    }
  }

  async function create(data: KnowledgeBaseCreate) {
    const kb = await createKnowledgeBase(data)
    await loadKnowledgeBases()
    return kb
  }

  async function update(id: number, data: KnowledgeBaseUpdate) {
    const kb = await updateKnowledgeBase(id, data)
    await refreshKnowledgeBase(id)
    return kb
  }

  async function remove(id: number) {
    await deleteKnowledgeBase(id)
    knowledgeBases.value = knowledgeBases.value.filter((kb) => kb.id !== id)
  }

  return {
    knowledgeBases,
    loading,
    error,
    kbCount,
    loadKnowledgeBases,
    getKnowledgeBase,
    refreshKnowledgeBase,
    create,
    update,
    remove,
  }
})
