<template>
  <div class="settings-page" v-if="kb">
    <div class="settings-grid">
      <!-- Settings form -->
      <section class="settings-card">
        <div class="settings-card__head">
          <span class="eyebrow">基础</span>
          <h2 class="settings-card__title">知识库信息</h2>
        </div>

        <form @submit.prevent="save" class="settings-form">
          <div class="field">
            <label class="field__label">名称</label>
            <input v-model="form.name" class="input" maxlength="100" required />
          </div>

          <div class="field">
            <label class="field__label">描述</label>
            <textarea v-model="form.description" class="textarea" rows="3" />
          </div>

          <div class="field">
            <label class="field__label">分块参数</label>
            <div class="field-row">
              <div class="mini-field">
                <span class="mini-field__label">分块大小</span>
                <input v-model.number="form.chunk_size" type="number" class="input" min="100" step="100" />
                <span class="mini-field__hint">默认 500 字符</span>
              </div>
              <div class="mini-field">
                <span class="mini-field__label">分块重叠</span>
                <input v-model.number="form.chunk_overlap" type="number" class="input" min="0" step="10" />
                <span class="mini-field__hint">默认 50 字符</span>
              </div>
            </div>
          </div>

          <div v-if="error" class="form-error">{{ error }}</div>
          <div v-if="success" class="form-success">已保存</div>

          <div class="form-actions">
            <button class="btn btn--ghost" type="button" @click="resetForm" :disabled="!dirty || saving">重置</button>
            <button class="btn btn--primary" type="submit" :disabled="!dirty || saving">
              {{ saving ? '保存中…' : '保存' }}
            </button>
          </div>
        </form>
      </section>

      <!-- Metadata + danger -->
      <aside class="settings-meta">
        <section class="meta-card">
          <span class="eyebrow">元数据</span>
          <dl class="meta-list">
            <div class="meta-row">
              <dt>编号</dt>
              <dd class="mono">#{{ String(kb.id).padStart(3, '0') }}</dd>
            </div>
            <div class="meta-row">
              <dt>可见范围</dt>
              <dd>
                <span class="badge" :class="`badge--${scopeVariant(kb.scope)}`">
                  <span class="dot" /> {{ SCOPE_LABELS[kb.scope] }}
                </span>
              </dd>
            </div>
            <div class="meta-row">
              <dt>状态</dt>
              <dd>
                <StatusDot :status="kb.status" />
                <span class="muted">{{ KB_STATUS_LABELS[kb.status] }}</span>
              </dd>
            </div>
            <div class="meta-row">
              <dt>创建时间</dt>
              <dd class="mono">{{ formatDate(kb.created_at) }}</dd>
            </div>
            <div class="meta-row">
              <dt>更新时间</dt>
              <dd class="mono">{{ formatDate(kb.updated_at) }}</dd>
            </div>
            <div class="meta-row">
              <dt>文档数</dt>
              <dd class="mono">{{ kb.document_count }}</dd>
            </div>
            <div class="meta-row">
              <dt>分块数</dt>
              <dd class="mono">{{ kb.chunk_count }}</dd>
            </div>
            <div v-if="kb.organization" class="meta-row">
              <dt>所属组织</dt>
              <dd>{{ kb.organization.name }}</dd>
            </div>
          </dl>
        </section>

        <section class="danger-card">
          <span class="eyebrow danger-text">危险操作</span>
          <h3 class="danger-card__title">删除知识库</h3>
          <p class="danger-card__desc">
            将永久删除该知识库、所有文档及其索引。不可恢复。
          </p>
          <button class="btn btn--danger" @click="confirmDelete = true">删除知识库</button>
        </section>
      </aside>
    </div>

    <!-- Delete confirm modal -->
    <transition name="fade">
      <div v-if="confirmDelete" class="modal-backdrop" @click.self="confirmDelete = false">
        <div class="confirm-dialog">
          <h3 class="confirm-dialog__title">永久删除？</h3>
          <p class="confirm-dialog__desc">
            将删除「<strong>{{ kb.name }}</strong>」及其 {{ kb.document_count }} 份文档。
            此操作不可撤销。
          </p>
          <div class="confirm-dialog__field">
            <label>输入知识库名称以确认：</label>
            <input v-model="confirmText" class="input" :placeholder="kb.name" />
          </div>
          <div class="confirm-dialog__actions">
            <button class="btn btn--ghost" @click="confirmDelete = false">取消</button>
            <button class="btn btn--danger" :disabled="confirmText !== kb.name" @click="doDelete">
              删除
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { deleteKnowledgeBase, fetchKnowledgeBase, updateKnowledgeBase } from '@/api/knowledge'
import StatusDot from '@/components/common/StatusDot.vue'
import { KB_STATUS_LABELS, SCOPE_LABELS } from '@/types/knowledge'
import type { KnowledgeBase, KnowledgeScope } from '@/types/knowledge'

const route = useRoute()
const router = useRouter()
const kbId = computed(() => Number(route.params.id))
const kb = ref<KnowledgeBase | null>(null)
const error = ref('')
const success = ref(false)
const saving = ref(false)
const confirmDelete = ref(false)
const confirmText = ref('')

const form = reactive({
  name: '',
  description: '',
  chunk_size: 500,
  chunk_overlap: 50,
})

async function load() {
  try {
    const data = await fetchKnowledgeBase(kbId.value)
    kb.value = data
    resetForm()
  } catch {
    /* ignore */
  }
}

function resetForm() {
  if (!kb.value) return
  form.name = kb.value.name
  form.description = kb.value.description || ''
  form.chunk_size = kb.value.chunk_size
  form.chunk_overlap = kb.value.chunk_overlap
  success.value = false
  error.value = ''
}

const dirty = computed(() => {
  if (!kb.value) return false
  return (
    form.name !== kb.value.name ||
    (form.description || '') !== (kb.value.description || '') ||
    form.chunk_size !== kb.value.chunk_size ||
    form.chunk_overlap !== kb.value.chunk_overlap
  )
})

async function save() {
  error.value = ''
  saving.value = true
  try {
    const updated = await updateKnowledgeBase(kbId.value, {
      name: form.name,
      description: form.description,
      chunk_size: form.chunk_size,
      chunk_overlap: form.chunk_overlap,
    })
    kb.value = updated
    success.value = true
    setTimeout(() => (success.value = false), 2000)
  } catch (e: any) {
    error.value = e?.response?.data?.detail || '保存失败'
  } finally {
    saving.value = false
  }
}

async function doDelete() {
  try {
    await deleteKnowledgeBase(kbId.value)
    confirmDelete.value = false
    router.push('/knowledge')
  } catch {
    /* ignore */
  }
}

function scopeVariant(s: KnowledgeScope) {
  return s === 'public' ? 'info' : s === 'org' ? 'accent' : 'success'
}

function formatDate(iso: string) {
  try {
    return new Date(iso).toLocaleString('zh-CN', { dateStyle: 'medium', timeStyle: 'short' })
  } catch {
    return iso
  }
}

watch(kbId, load)
onMounted(load)
</script>

<style lang="scss" scoped>
@use '@/styles/tokens' as *;

.settings-page {
  max-width: 1080px;
  margin: 0 auto;
}

.settings-grid {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: $s-6;
  align-items: flex-start;
}

.settings-card {
  background: $bg-surface;
  border: 1px solid $border-subtle;
  border-radius: $r-lg;
  padding: $s-6;

  &__head {
    margin-bottom: $s-5;
    padding-bottom: $s-4;
    border-bottom: 1px solid $border-subtle;
  }
  &__title {
    font-family: $font-display;
    font-size: $fs-24;
    font-weight: $fw-semibold;
    margin-top: $s-2;
    letter-spacing: -0.01em;
  }
}

.settings-form {
  display: flex;
  flex-direction: column;
  gap: $s-4;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: $s-2;
  padding-top: $s-3;
  border-top: 1px solid $border-subtle;
}

.field {
  display: flex;
  flex-direction: column;
  gap: $s-2;

  &__label {
    font-size: $fs-13;
    font-weight: $fw-medium;
    color: $text-secondary;
  }
}

.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: $s-3;
}

.mini-field {
  display: flex;
  flex-direction: column;
  gap: $s-1;
  padding: $s-3;
  background: $bg-inset;
  border: 1px solid $border-subtle;
  border-radius: $r-md;

  &__label {
    font-size: $fs-12;
    color: $text-secondary;
    font-weight: $fw-medium;
  }
  &__hint {
    font-size: $fs-12;
    color: $text-tertiary;
  }
}

.form-error, .form-success {
  padding: $s-3 $s-4;
  border-radius: $r-md;
  font-size: $fs-13;
}
.form-error { background: $danger-soft; color: $danger; }
.form-success {
  background: $success-soft;
  color: $success;
}

.settings-meta {
  display: flex;
  flex-direction: column;
  gap: $s-4;
}

.meta-card {
  background: $bg-surface;
  border: 1px solid $border-subtle;
  border-radius: $r-lg;
  padding: $s-5;

  .eyebrow { display: block; margin-bottom: $s-4; color: $accent; }
}

.meta-list {
  display: flex;
  flex-direction: column;
  gap: 0;
  margin: 0;
}

.meta-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: $s-3 0;
  border-bottom: 1px solid $border-subtle;
  font-size: $fs-13;

  &:last-child { border-bottom: none; }
  dt { color: $text-tertiary; margin: 0; }
  dd { color: $text-primary; margin: 0; display: flex; align-items: center; gap: $s-2; }
}

.danger-card {
  background: $bg-surface;
  border: 1px solid rgba(229, 72, 77, 0.3);
  border-radius: $r-lg;
  padding: $s-5;

  .danger-text { color: $danger; display: block; margin-bottom: $s-3; }

  &__title {
    font-family: $font-display;
    font-size: $fs-17;
    font-weight: $fw-semibold;
    margin-bottom: $s-2;
  }
  &__desc {
    color: $text-secondary;
    font-size: $fs-13;
    line-height: $lh-snug;
    margin-bottom: $s-4;
  }
}

.modal-backdrop {
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
  width: 440px;
  background: $bg-surface;
  border: 1px solid $border-strong;
  border-radius: $r-lg;
  padding: $s-6;
  box-shadow: $shadow-lg;

  &__title {
    font-family: $font-display;
    font-size: $fs-24;
    font-weight: $fw-semibold;
    margin-bottom: $s-2;
  }
  &__desc {
    color: $text-secondary;
    font-size: $fs-14;
    line-height: $lh-snug;
    margin-bottom: $s-4;
    strong { color: $danger; }
  }
  &__field {
    display: flex;
    flex-direction: column;
    gap: $s-2;
    margin-bottom: $s-4;
    label {
      font-size: $fs-13;
      color: $text-secondary;
    }
  }
  &__actions {
    display: flex;
    justify-content: flex-end;
    gap: $s-2;
  }
}

.danger-text { color: $danger; }

.fade-enter-active, .fade-leave-active { transition: opacity $dur-base $ease-out; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

@media (max-width: 900px) {
  .settings-grid { grid-template-columns: 1fr; }
}
</style>