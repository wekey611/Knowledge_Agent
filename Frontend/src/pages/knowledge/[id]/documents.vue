<template>
  <div
    class="docs-page"
    @dragover.prevent="onPageDragOver"
    @dragleave.prevent="onPageDragLeave"
    @drop.prevent="handleDrop"
  >
    <input
      ref="fileInput"
      type="file"
      class="docs-page__file-input"
      :accept="acceptTypes"
      multiple
      @change="handleFileSelect"
    />
    <!-- Drop zone -->
    <div
      v-if="canManage"
      class="dropzone"
      :class="{ 'dropzone--dragging': isDragging, 'dropzone--uploading': uploading }"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @click="fileInput?.click()"
    >
      <div class="dropzone__icon">
        <svg viewBox="0 0 32 32" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M16 22V8M10 14l6-6 6 6" stroke-linecap="round" stroke-linejoin="round" />
          <path d="M4 22v4a2 2 0 0 0 2 2h20a2 2 0 0 0 2-2v-4" stroke-linecap="round" />
        </svg>
      </div>
      <p class="dropzone__main">
        {{ uploading ? '正在上传…' : '拖拽文件到此处，或' }}
        <span v-if="!uploading" class="dropzone__link">点击选择</span>
      </p>
      <p class="dropzone__hint">PDF · Word · Markdown · TXT · HTML · 单文件 ≤ 50MB</p>

      <div v-if="uploading" class="dropzone__progress">
        <div class="progress-bar">
          <div class="progress-bar__fill" :style="{ width: uploadProgress + '%' }" />
        </div>
        <span class="progress-text mono">{{ uploadProgress }}%</span>
      </div>
    </div>

    <!-- Document list -->
    <div v-if="listLoading" class="docs-list">
      <div v-for="i in 3" :key="i" class="docs-list__skel" />
    </div>

    <div v-else-if="documents.length === 0" class="docs-empty">
      <EmptyState
        v-if="canManage"
        title="还没有文档"
        description="上传你的第一个文档，解析后即可在对话 Tab 中向它提问。支持 PDF / Word / Markdown / TXT / HTML，单文件不超过 50MB。"
      >
        <template #icon>
          <svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" />
            <path d="M14 3v6h6" />
          </svg>
        </template>
        <template #action>
          <button class="btn btn--primary btn--lg" @click="fileInput?.click()">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 5v14M5 12h14" stroke-linecap="round" />
            </svg>
            上传第一个文档
          </button>
          <p class="docs-empty__tip">也可以把文件直接拖到本页任意位置</p>
        </template>
      </EmptyState>

      <EmptyState
        v-else
        title="还没有文档"
        :description="`你当前是此知识库的 ${canManage ? '' : '只读'}成员，上传和删除需要创建者权限。`"
      >
        <template #icon>
          <svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="currentColor" stroke-width="1.5">
            <rect x="3" y="11" width="18" height="11" rx="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
        </template>
      </EmptyState>
    </div>

    <div v-else class="docs-list">
      <div class="docs-list__head">
        <span class="eyebrow">文档</span>
        <span class="muted">{{ documents.length }} 份 · 共 {{ totalChunks }} 个分块</span>
      </div>

      <article v-for="doc in documents" :key="doc.id" class="doc-row">
        <div class="doc-row__icon" :style="{ color: fileTypeColor(doc.filename), background: fileTypeBg(doc.filename) }">
          <span class="mono">{{ fileExt(doc.filename).toUpperCase().slice(0, 4) }}</span>
        </div>

        <div class="doc-row__main">
          <h4 class="doc-row__title">{{ doc.title }}</h4>
          <div class="doc-row__meta">
            <span class="mono">{{ formatSize(doc.file_size) }}</span>
            <span class="faint">·</span>
            <span class="mono">{{ doc.chunk_count }} 块</span>
            <span class="faint">·</span>
            <span class="mono">更新于 {{ formatDate(doc.updated_at) }}</span>
          </div>
        </div>

        <span class="badge" :class="`badge--${statusVariant(doc.parser_status)}`">
          <span class="dot" />
          {{ PARSER_STATUS_LABELS[doc.parser_status] }}
        </span>

        <div class="doc-row__actions">
          <button class="btn btn--ghost btn--icon btn--sm" @click="openPreview(doc)" title="预览">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/></svg>
          </button>
          <button v-if="canManage" class="btn btn--ghost btn--icon btn--sm" @click="handleDownload(doc)" title="下载">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 4v12M6 12l6 6 6-6M4 20h16" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </button>
          <button v-if="canManage" class="btn btn--danger btn--icon btn--sm" @click="handleDelete(doc)" title="删除">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 7h16M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2M6 7l1 12a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-12" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </button>
        </div>
      </article>
    </div>

    <!-- Delete confirm modal -->
    <transition name="fade">
      <div v-if="confirming" class="confirm-backdrop" @click.self="confirming = null">
        <div class="confirm-dialog">
          <h3 class="confirm-dialog__title">确认删除</h3>
          <p class="confirm-dialog__desc">将永久删除「<strong>{{ confirming.title }}</strong>」及其索引，不可恢复。</p>
          <div class="confirm-dialog__actions">
            <button class="btn btn--ghost" @click="confirming = null">取消</button>
            <button class="btn btn--danger" @click="confirmDelete">删除</button>
          </div>
        </div>
      </div>
    </transition>

    <DocumentPreviewDrawer
      v-model="drawerOpen"
      :doc="previewingDoc"
      :src="previewUrl"
      :preview-key="previewKey"
      @fullscreen="openFullscreen"
    />

    <DocumentPreviewModal
      v-model="modalOpen"
      :doc="previewingDoc"
      :src="previewUrl"
      :preview-key="previewKey"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { deleteDocument, downloadDocument, fetchDocuments, previewDocument, uploadDocument } from '@/api/document'
import { showToast } from '@/api/http'
import EmptyState from '@/components/common/EmptyState.vue'
import DocumentPreviewDrawer from '@/components/knowledge/DocumentPreviewDrawer.vue'
import DocumentPreviewModal from '@/components/knowledge/DocumentPreviewModal.vue'
import { PARSER_STATUS_LABELS } from '@/types/knowledge'
import type { DocumentSimple, ParserStatus } from '@/types/knowledge'

const props = defineProps<{ kbId: number; canManage?: boolean }>()

const documents = ref<DocumentSimple[]>([])
const listLoading = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const confirming = ref<DocumentSimple | null>(null)

// 预览状态
const drawerOpen = ref(false)
const modalOpen = ref(false)
const previewingDoc = ref<DocumentSimple | null>(null)
const previewUrl = ref<string | null>(null)
const previewKey = ref(0)

const acceptTypes = '.pdf,.doc,.docx,.md,.markdown,.txt,.html,.htm'
const MAX_SIZE_MB = 50

const totalChunks = computed(() => documents.value.reduce((s, d) => s + d.chunk_count, 0))

async function loadDocuments() {
  if (!props.kbId || Number.isNaN(props.kbId)) {
    documents.value = []
    return
  }
  listLoading.value = true
  try {
    const res = await fetchDocuments(props.kbId)
    documents.value = res.data
  } catch {
    documents.value = []
  } finally {
    listLoading.value = false
  }
}

function handleDrop(e: DragEvent) {
  isDragging.value = false
  if (!props.canManage) return
  const files = Array.from(e.dataTransfer?.files || [])
  if (files.length > 0) handleFiles(files)
}

function onPageDragOver(e: DragEvent) {
  if (!props.canManage) return
  if (e.dataTransfer?.types?.includes('Files')) {
    isDragging.value = true
  }
}

function onPageDragLeave(e: DragEvent) {
  // 只在离开整个页面时清除
  if (e.relatedTarget === null) isDragging.value = false
}

function handleFileSelect(e: Event) {
  const input = e.target as HTMLInputElement
  const files = Array.from(input.files || [])
  if (files.length > 0) handleFiles(files)
  input.value = ''
}

async function handleFiles(files: File[]) {
  const oversized = files.find((f) => f.size > MAX_SIZE_MB * 1024 * 1024)
  if (oversized) {
    showToast(`「${oversized.name}」超过 ${MAX_SIZE_MB}MB 限制`)
    return
  }
  uploading.value = true
  uploadProgress.value = 0
  let success = 0
  let lastError = ''
  for (const file of files) {
    try {
      await uploadDocument(props.kbId, file)
      success++
      uploadProgress.value = Math.round((success / files.length) * 100)
    } catch (e: any) {
      lastError =
        e?.response?.data?.detail ||
        e?.message ||
        '上传失败'
      console.error('[upload] failed:', file.name, e)
    }
  }
  uploading.value = false
  uploadProgress.value = 0
  if (success > 0) {
    showToast(success === files.length ? `已上传 ${success} 个文档` : `成功 ${success}/${files.length}`, 'success')
    await loadDocuments()
  } else {
    showToast(`上传失败：${lastError}`)
  }
}

async function handleDownload(doc: DocumentSimple) {
  try {
    await downloadDocument(props.kbId, doc.id, doc.filename)
  } catch (e: any) {
    showToast(`下载失败：${e?.response?.data?.detail || e?.message || '未知错误'}`)
  }
}

function handleDelete(doc: DocumentSimple) {
  confirming.value = doc
}

function cleanupPreview() {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
    previewUrl.value = null
  }
  previewingDoc.value = null
}

let previewSeq = 0

async function openPreview(doc: DocumentSimple) {
  const seq = ++previewSeq
  previewingDoc.value = doc
  previewUrl.value = null
  drawerOpen.value = true
  previewKey.value++
  try {
    const url = await previewDocument(props.kbId, doc.id)
    // 期间用户可能已经打开了别的预览/关闭了抽屉
    if (seq !== previewSeq) {
      URL.revokeObjectURL(url)
      return
    }
    previewUrl.value = url
  } catch {
    if (seq === previewSeq) previewUrl.value = null
  }
}

function openFullscreen() {
  modalOpen.value = true
}

watch([drawerOpen, modalOpen], ([drawer, modal]) => {
  if (!drawer && !modal) {
    // 都关掉了再清理
    setTimeout(cleanupPreview, 300)
  }
})

onBeforeUnmount(cleanupPreview)

async function confirmDelete() {
  if (!confirming.value) return
  const doc = confirming.value
  confirming.value = null
  try {
    await deleteDocument(props.kbId, doc.id)
    showToast('文档已删除', 'success')
    await loadDocuments()
  } catch (e: any) {
    showToast(`删除失败：${e?.response?.data?.detail || e?.message || '未知错误'}`)
  }
}

function fileExt(name: string) {
  return name.split('.').pop() || ''
}

function fileTypeColor(name: string): string {
  const ext = fileExt(name).toLowerCase()
  const map: Record<string, string> = {
    pdf: '#E5484D',
    doc: '#6B9DD9',
    docx: '#6B9DD9',
    md: '#A8E6CF',
    markdown: '#A8E6CF',
    txt: '#9AA0A6',
    html: '#F5A623',
    htm: '#F5A623',
  }
  return map[ext] || '#9AA0A6'
}

function fileTypeBg(name: string): string {
  const color = fileTypeColor(name)
  return color + '1A'
}

function statusVariant(s: ParserStatus): string {
  if (s === 'completed') return 'success'
  if (s === 'failed') return 'danger'
  if (s === 'waiting') return ''
  return 'info'
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
  } catch {
    return iso
  }
}

watch(() => props.kbId, loadDocuments)
onMounted(loadDocuments)
</script>

<style lang="scss" scoped>
@use '@/styles/tokens' as *;

.docs-page {
  max-width: 880px;
  margin: 0 auto;
  &__file-input { display: none; }
}

.dropzone {
  border: 2px dashed $border-strong;
  border-radius: $r-lg;
  background: $bg-surface;
  padding: $s-10 $s-6;
  text-align: center;
  cursor: pointer;
  transition: all $dur-base $ease-out;
  margin-bottom: $s-6;

  &__icon {
    width: 56px;
    height: 56px;
    margin: 0 auto $s-3;
    border-radius: $r-md;
    background: $accent-soft;
    color: $accent;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  &__main {
    font-size: $fs-15;
    color: $text-primary;
    font-weight: $fw-medium;
    margin-bottom: $s-1;
  }
  &__link {
    color: $accent;
    text-decoration: underline;
    text-underline-offset: 3px;
  }
  &__hint {
    font-size: $fs-12;
    color: $text-tertiary;
  }
  &__progress {
    margin-top: $s-4;
    max-width: 320px;
    margin-left: auto;
    margin-right: auto;
  }

  &:hover, &--dragging {
    border-color: $accent;
    background: $accent-soft;
  }
  &--uploading { pointer-events: none; }
}

.progress-bar {
  height: 4px;
  background: $bg-elevated;
  border-radius: $r-pill;
  overflow: hidden;

  &__fill {
    height: 100%;
    background: $accent;
    transition: width $dur-base $ease-out;
  }
}
.progress-text {
  display: block;
  margin-top: $s-1;
  font-size: $fs-12;
  color: $text-tertiary;
}

.docs-list {
  background: $bg-surface;
  border: 1px solid $border-subtle;
  border-radius: $r-lg;
  overflow: hidden;

  &__head {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    padding: $s-4 $s-5;
    border-bottom: 1px solid $border-subtle;
    .eyebrow { color: $accent; }
  }

  &__skel {
    height: 80px;
    margin: $s-2;
    background: linear-gradient(90deg, $bg-surface 0%, $bg-elevated 50%, $bg-surface 100%);
    background-size: 200% 100%;
    border-radius: $r-md;
    animation: shimmer 1.6s linear infinite;
  }
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.doc-row {
  display: flex;
  align-items: center;
  gap: $s-4;
  padding: $s-4 $s-5;
  border-bottom: 1px solid $border-subtle;
  transition: background $dur-base $ease-out;

  &:last-child { border-bottom: none; }
  &:hover { background: $bg-elevated; }

  &__icon {
    width: 44px;
    height: 44px;
    flex-shrink: 0;
    border-radius: $r-md;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: $font-mono;
    font-size: $fs-12;
    font-weight: $fw-semibold;
  }
  &__main { flex: 1; min-width: 0; }
  &__title {
    font-size: $fs-14;
    font-weight: $fw-medium;
    color: $text-primary;
    margin-bottom: $s-1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  &__meta {
    display: flex;
    align-items: center;
    gap: $s-2;
    font-size: $fs-12;
    color: $text-secondary;
  }
  &__actions {
    display: flex;
    gap: $s-1;
  }
}

.docs-empty {
  background: $bg-surface;
  border: 1px dashed $border-strong;
  border-radius: $r-lg;
  padding: $s-4;
}
.docs-empty__tip {
  margin-top: $s-3;
  font-size: $fs-12;
  color: $text-tertiary;
}

.confirm-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}
.confirm-dialog {
  width: 360px;
  background: $bg-surface;
  border: 1px solid $border-strong;
  border-radius: $r-lg;
  padding: $s-6;
  box-shadow: $shadow-lg;

  &__title {
    font-family: $font-display;
    font-size: $fs-20;
    font-weight: $fw-semibold;
    margin-bottom: $s-2;
  }
  &__desc {
    color: $text-secondary;
    font-size: $fs-14;
    line-height: $lh-snug;
    margin-bottom: $s-5;
    strong { color: $accent; }
  }
  &__actions {
    display: flex;
    justify-content: flex-end;
    gap: $s-2;
  }
}

.fade-enter-active, .fade-leave-active { transition: opacity $dur-base $ease-out; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>