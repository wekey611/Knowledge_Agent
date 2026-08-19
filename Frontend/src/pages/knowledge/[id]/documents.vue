<template>
  <div class="doc-page-wrap">
    <!-- Loading -->
    <EmptyState v-if="kbLoading" type="loading" title="加载知识库..." />

    <!-- Not found -->
    <EmptyState
      v-else-if="!knowledgeBase"
      type="error"
      title="知识库未找到"
      description="请返回仪表盘选择有效的知识库"
      action-label="返回仪表盘"
      @action="$router.push('/dashboard')"
    />

    <div v-else class="doc-page">
      <!-- Header -->
      <header class="doc-header">
        <div class="doc-header-text">
          <h2 class="doc-title">{{ knowledgeBase.name }} <span class="doc-title-sep">·</span> 文档</h2>
          <p class="doc-desc">
            <template v-if="documents.length > 0">共 {{ documents.length }} 个文档</template>
            <template v-else>还没有文档</template>
          </p>
        </div>
        <el-button
          v-if="canManage"
          type="primary"
          :icon="UploadFilled"
          :loading="uploading"
          @click="fileInput?.click()"
        >
          上传文档
        </el-button>
        <input
          ref="fileInput"
          type="file"
          class="hidden-input"
          :accept="acceptTypes"
          multiple
          @change="handleFileSelect"
        />
      </header>

      <!-- Upload dropzone（仅创建者可见） -->
      <div
        v-if="canManage"
        class="dropzone"
        :class="{ 'is-dragging': isDragging, 'is-uploading': uploading }"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="handleDrop"
        @click="fileInput?.click()"
      >
        <div class="dropzone-icon">
          <el-icon :size="28"><UploadFilled /></el-icon>
        </div>
        <p class="dropzone-main">
          拖拽文件到此处，或 <span class="dropzone-link">点击选择文件</span>
        </p>
        <p class="dropzone-sub">支持 PDF、Word、Markdown、TXT、HTML（可多选）</p>
      </div>

      <!-- Upload progress -->
      <div v-if="uploadProgress > 0 && uploading" class="upload-progress">
        <el-progress :percentage="uploadProgress" :stroke-width="6" />
      </div>

      <!-- List loading -->
      <div v-if="listLoading" class="doc-list">
        <div v-for="i in 4" :key="i" class="doc-row skeleton-row">
          <div class="skeleton skeleton-icon" />
          <div class="doc-info">
            <div class="skeleton skeleton-title" />
            <div class="skeleton skeleton-meta" />
          </div>
          <div class="skeleton skeleton-tag" />
        </div>
      </div>

      <!-- Empty -->
      <EmptyState
        v-else-if="documents.length === 0"
        type="empty"
        title="暂无文档"
        description="上传你的第一个文档，开始构建知识库"
      />

      <!-- Document list -->
      <div v-else class="doc-list">
        <div v-for="doc in documents" :key="doc.id" class="doc-row">
          <div class="doc-icon" :style="{ color: fileTypeColor(doc.filename) }">
            <el-icon :size="20"><Document /></el-icon>
          </div>

          <div class="doc-info">
            <span class="doc-name" :title="doc.filename">{{ doc.filename }}</span>
            <span class="doc-meta">
              {{ formatSize(doc.file_size) }} · {{ doc.chunk_count }} 分块 · 更新于 {{ formatDate(doc.updated_at) }}
            </span>
          </div>

          <span
            class="status-tag"
            :style="{
              color: PARSER_STATUS_COLORS[doc.parser_status],
              background: `${PARSER_STATUS_COLORS[doc.parser_status]}1A`,
            }"
          >
            <span class="status-dot" :style="{ background: PARSER_STATUS_COLORS[doc.parser_status] }" />
            {{ PARSER_STATUS_LABELS[doc.parser_status] }}
          </span>

          <div class="doc-actions">
            <el-tooltip content="下载">
              <el-button size="small" :icon="Download" circle @click="handleDownload(doc)" />
            </el-tooltip>
            <el-tooltip v-if="canManage" content="删除">
              <el-button size="small" type="danger" :icon="Delete" circle @click="handleDelete(doc)" />
            </el-tooltip>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Document, Download, UploadFilled } from '@element-plus/icons-vue'
import type { KnowledgeBaseSimple, DocumentSimple } from '@/types/knowledge'
import {
  PARSER_STATUS_COLORS,
  PARSER_STATUS_LABELS,
} from '@/types/knowledge'
import {
  deleteDocument,
  downloadDocument,
  fetchDocuments,
  uploadDocument,
} from '@/api/document'
import EmptyState from '@/components/common/EmptyState.vue'

const props = defineProps<{
  knowledgeBase: KnowledgeBaseSimple | null
  kbLoading: boolean
  /** 当前用户是否为 KB 创建者（决定上传/删除权限） */
  canManage: boolean
}>()

const emit = defineEmits<{
  /** 文档数量变化，通知父级刷新侧边栏与 KB 统计 */
  'documents-changed': []
}>()

const kbId = computed(() => props.knowledgeBase?.id)

const documents = ref<DocumentSimple[]>([])
const listLoading = ref(false)

// 上传状态
const fileInput = ref<HTMLInputElement>()
const isDragging = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)

const acceptTypes =
  '.pdf,.doc,.docx,.md,.markdown,.txt,.html,.htm'

const MAX_SIZE_MB = 50

async function loadDocuments() {
  if (!kbId.value) return
  listLoading.value = true
  try {
    const res = await fetchDocuments(kbId.value)
    documents.value = res.data
  } catch {
    documents.value = []
  } finally {
    listLoading.value = false
  }
}

function handleDrop(e: DragEvent) {
  isDragging.value = false
  const files = Array.from(e.dataTransfer?.files || [])
  if (files.length > 0) handleFiles(files)
}

function handleFileSelect(e: Event) {
  const files = Array.from((e.target as HTMLInputElement).files || [])
  if (files.length > 0) handleFiles(files)
  ;(e.target as HTMLInputElement).value = ''
}

async function handleFiles(files: File[]) {
  const oversized = files.find((f) => f.size > MAX_SIZE_MB * 1024 * 1024)
  if (oversized) {
    ElMessage.error(`「${oversized.name}」超过 ${MAX_SIZE_MB}MB 限制`)
    return
  }
  uploading.value = true
  uploadProgress.value = 0
  let success = 0
  try {
    for (const file of files) {
      try {
        await uploadDocument(kbId.value!, file)
        success++
        uploadProgress.value = Math.round((success / files.length) * 100)
      } catch {
        ElMessage.error(`「${file.name}」上传失败`)
      }
    }
    if (success > 0) {
      ElMessage.success(`成功上传 ${success} 个文档`)
      await loadDocuments()
      emit('documents-changed')
    }
  } finally {
    uploading.value = false
    uploadProgress.value = 0
  }
}

async function handleDownload(doc: DocumentSimple) {
  try {
    await downloadDocument(kbId.value!, doc.id, doc.filename)
  } catch {
    // 拦截器已提示
  }
}

async function handleDelete(doc: DocumentSimple) {
  try {
    await ElMessageBox.confirm(
      `确定删除「${doc.filename}」吗？删除后不可恢复。`,
      '删除确认',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }
    )
  } catch {
    return
  }
  try {
    await deleteDocument(kbId.value!, doc.id)
    ElMessage.success('文档已删除')
    await loadDocuments()
    emit('documents-changed')
  } catch {
    // 拦截器已提示
  }
}

function fileTypeColor(filename: string): string {
  const ext = filename.split('.').pop()?.toLowerCase()
  const map: Record<string, string> = {
    pdf: '#EF4444',
    doc: '#2563EB',
    docx: '#2563EB',
    md: '#8B5CF6',
    txt: '#64748B',
    html: '#F97316',
    htm: '#F97316',
  }
  return map[ext || ''] || 'var(--color-muted-foreground)'
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

watch(kbId, () => loadDocuments())
onMounted(loadDocuments)
</script>

<style scoped>
.doc-page-wrap {
  height: 100%;
  overflow-y: auto;
}

.doc-page {
  max-width: 960px;
  margin: 0 auto;
  padding: var(--space-8) var(--space-7) var(--space-12);
}

/* Header */
.doc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-7);
}

.doc-title {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-foreground);
  margin-bottom: var(--space-2);
}

.doc-title-sep {
  color: var(--color-border);
  font-weight: 400;
}

.doc-desc {
  font-size: var(--text-sm);
  color: var(--color-muted-foreground);
}

.hidden-input {
  display: none;
}

/* Dropzone */
.dropzone {
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-xl);
  background: var(--color-card);
  padding: var(--space-10) var(--space-6);
  text-align: center;
  cursor: pointer;
  transition: all var(--transition-normal);
  margin-bottom: var(--space-7);
}

.dropzone:hover,
.dropzone.is-dragging {
  border-color: var(--color-primary);
  background: var(--color-primary-bg);
}

.dropzone.is-uploading {
  pointer-events: none;
  opacity: 0.7;
}

.dropzone-icon {
  display: flex;
  justify-content: center;
  margin-bottom: var(--space-4);
  color: var(--color-primary);
}

.dropzone-main {
  font-size: var(--text-base);
  font-weight: 500;
  color: var(--color-foreground);
  margin-bottom: var(--space-2);
}

.dropzone-link {
  color: var(--color-primary);
}

.dropzone-sub {
  font-size: var(--text-xs);
  color: var(--color-muted-foreground);
}

/* Upload progress */
.upload-progress {
  margin-bottom: var(--space-5);
}

/* List */
.doc-list {
  background: var(--color-card);
  border-radius: var(--radius-lg);
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
  border: 1px solid var(--color-border-light);
  overflow: hidden;
}

.doc-row {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--color-border-light);
  transition: background var(--transition-fast);
}

.doc-row:last-child {
  border-bottom: none;
}

.doc-row:hover {
  background: var(--color-muted);
}

.doc-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  background: var(--color-muted);
  flex-shrink: 0;
}

.doc-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.doc-name {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-foreground);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.doc-meta {
  font-size: var(--text-xs);
  color: var(--color-muted-foreground);
}

/* Status tag（状态色更明显：浅色底 + 彩色文字 + 圆点） */
.status-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 500;
  flex-shrink: 0;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: var(--radius-full);
}

.doc-actions {
  display: flex;
  gap: var(--space-2);
  flex-shrink: 0;
}

/* Skeleton */
.skeleton-row {
  cursor: default;
}

.skeleton {
  border-radius: var(--radius-sm);
  background: var(--color-muted);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.skeleton-icon {
  width: 40px;
  height: 40px;
}

.skeleton-title {
  width: 200px;
  height: 14px;
  margin-bottom: var(--space-2);
}

.skeleton-meta {
  width: 140px;
  height: 12px;
}

.skeleton-tag {
  width: 72px;
  height: 22px;
  border-radius: var(--radius-full);
}

@keyframes skeleton-pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}
</style>
