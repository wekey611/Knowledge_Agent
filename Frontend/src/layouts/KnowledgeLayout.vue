<template>
  <div class="knowledge-layout">
    <!-- Left: Document sidebar -->
    <KnowledgeSidebar
      :knowledge-base="knowledgeBase"
      :documents="documents"
      :loading="docsLoading"
      :active-doc-id="activeDocId"
      @select-doc="selectDoc"
    />

    <!-- Center: Chat area -->
    <div class="chat-area">
      <router-view
        :knowledge-base="knowledgeBase"
        :kb-loading="kbLoading"
        :can-manage="canManage"
        :messages="messages"
        :messages-loading="msgsLoading"
        :sending="sending"
        :error="chatError"
        @send="handleSend"
        @load-messages="loadMessages"
        @retry-message="handleRetry"
        @suggest="handleSuggest"
        @documents-changed="reloadDocuments"
      />
    </div>

    <!-- Right: Context panel (preview selected doc) -->
    <div v-if="activeDocId" class="context-panel">
      <div class="context-header">
        <h4 class="context-title">文档预览</h4>
        <button class="context-close" @click="activeDocId = null">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>
      <div class="context-body">
        <EmptyState
          v-if="!activeDoc"
          type="empty"
          title="选择文档"
          description="从左侧选择一个文档以预览"
        />
        <div v-else class="doc-preview">
          <div class="doc-preview-header">
            <el-tag size="small">{{ fileExt(activeDoc.filename) }}</el-tag>
            <span class="doc-size">{{ formatSize(activeDoc.file_size) }}</span>
          </div>
          <p class="doc-preview-title">{{ activeDoc.filename }}</p>
          <p class="doc-preview-meta">
            更新于 {{ formatDate(activeDoc.updated_at) }}
          </p>
          <div class="doc-preview-placeholder">
            <p>文档内容预览功能将在后续版本中提供</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { KnowledgeBaseSimple, DocumentSimple, ChatMessage } from '@/types/knowledge'
import { useAuthStore } from '@/stores/auth'
import { useKnowledgeStore } from '@/stores/knowledge'
import { useChatStore } from '@/stores/chat'
import { fetchDocuments as fetchDocumentList } from '@/api/document'
import KnowledgeSidebar from '@/components/knowledge/KnowledgeSidebar.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const route = useRoute()
const authStore = useAuthStore()
const knowledgeStore = useKnowledgeStore()
const chatStore = useChatStore()

const kbId = computed(() => parseInt(route.params.id as string))
const kbLoading = ref(false)
const docsLoading = ref(false)
const documents = ref<DocumentSimple[]>([])
const activeDocId = ref<number | null>(null)
/** KB 创建者 id（从详情接口获取，用于前端权限控制） */
const kbOwnerId = ref<number | null>(null)

const canManage = computed(
  () => kbOwnerId.value !== null && kbOwnerId.value === authStore.user?.id
)

const knowledgeBase = computed<KnowledgeBaseSimple | null>(() => {
  return knowledgeStore.getKnowledgeBase(kbId.value) || null
})

const messages = computed<ChatMessage[]>(() => {
  return chatStore.getMessages(kbId.value)
})

const msgsLoading = computed(() => chatStore.loading)
const sending = computed(() => chatStore.sending)
const chatError = computed(() => chatStore.error)

const activeDoc = computed(() => {
  if (!activeDocId.value) return null
  return documents.value.find((d) => d.id === activeDocId.value) || null
})

function selectDoc(id: number) {
  activeDocId.value = activeDocId.value === id ? null : id
}

async function loadMessages() {
  await chatStore.loadMessages(kbId.value)
}

async function handleSend(content: string) {
  const success = await chatStore.send(kbId.value, content)
  if (!success && chatStore.error) {
    ElMessage.error(chatStore.error)
  }
}

function handleRetry(_msg: ChatMessage) {
  ElMessage.info('重试功能将在后续版本完善')
}

function handleSuggest(question: string) {
  handleSend(question)
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleDateString('zh-CN')
  } catch {
    return dateStr
  }
}

function fileExt(filename: string): string {
  const ext = filename.split('.').pop()
  return ext ? ext.toUpperCase() : 'FILE'
}

// 加载文档列表 + KB 创建者（决定上传/删除权限）
async function loadDocsAndOwner(id: number) {
  docsLoading.value = true
  try {
    const res = await fetchDocumentList(id)
    documents.value = res.data
  } catch {
    documents.value = []
  } finally {
    docsLoading.value = false
  }
  const detail = await knowledgeStore.refreshKnowledgeBase(id)
  kbOwnerId.value = detail?.owner_id ?? null
}

/** 文档数量变化后刷新（上传/删除后由 documents.vue 触发） */
async function reloadDocuments() {
  const id = kbId.value
  if (!id) return
  await loadDocsAndOwner(id)
}

// Load KB info and documents when route changes
watch(kbId, async (id) => {
  activeDocId.value = null

  // Ensure KB is loaded
  if (!knowledgeStore.getKnowledgeBase(id) && knowledgeStore.knowledgeBases.length === 0) {
    kbLoading.value = true
    await knowledgeStore.loadKnowledgeBases()
    kbLoading.value = false
  }

  // Load documents + owner
  await loadDocsAndOwner(id)

  // Load chat messages
  loadMessages()
}, { immediate: true })
</script>

<style scoped>
.knowledge-layout {
  display: flex;
  height: 100%;
  overflow: hidden;
  background: var(--color-bg);
}

.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}

/* Context panel (right) */
.context-panel {
  width: 320px;
  min-width: 320px;
  background: var(--color-card);
  border-left: 1px solid var(--color-border-light);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.context-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-5);
  border-bottom: 1px solid var(--color-border-light);
}

.context-title {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-foreground);
}

.context-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  border: none;
  background: transparent;
  color: var(--color-muted-foreground);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.context-close:hover {
  background: var(--color-muted);
  color: var(--color-foreground);
}

.context-body {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-5);
}

.doc-preview-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.doc-size {
  font-size: var(--text-xs);
  color: var(--color-muted-foreground);
}

.doc-preview-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-foreground);
  margin-bottom: var(--space-2);
}

.doc-preview-meta {
  font-size: var(--text-xs);
  color: var(--color-muted-foreground);
  margin-bottom: var(--space-6);
}

.doc-preview-placeholder {
  padding: var(--space-8) var(--space-5);
  text-align: center;
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-muted-foreground);
  font-size: var(--text-sm);
}
</style>
