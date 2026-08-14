<template>
  <el-dialog
    :model-value="modelValue"
    :title="isEdit ? '编辑知识库' : '创建知识库'"
    width="520px"
    :close-on-click-modal="false"
    @update:model-value="$emit('update:modelValue', $event)"
    @closed="handleClosed"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="96px" label-position="left">
      <el-form-item label="名称" prop="name">
        <el-input
          v-model="form.name"
          placeholder="知识库名称"
          maxlength="100"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="描述" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="3"
          placeholder="描述这个知识库的用途（可选）"
        />
      </el-form-item>

      <el-form-item v-if="!isEdit" label="可见范围" prop="scope">
        <el-radio-group v-model="form.scope">
          <el-radio value="personal">个人</el-radio>
          <el-radio value="org" :disabled="organizations.length === 0">组织</el-radio>
          <el-radio v-if="isAdmin" value="public">公开</el-radio>
        </el-radio-group>
        <div v-if="form.scope === 'org' && organizations.length === 0" class="form-hint">
          你还没有加入任何组织，请先创建或加入组织
        </div>
      </el-form-item>

      <el-form-item v-if="!isEdit && form.scope === 'org'" label="所属组织" prop="org_id">
        <el-select v-model="form.org_id" placeholder="选择组织" style="width: 100%">
          <el-option
            v-for="org in organizations"
            :key="org.id"
            :label="org.name"
            :value="org.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="分块大小" prop="chunk_size">
        <el-input-number v-model="form.chunk_size" :min="100" :step="100" />
        <span class="form-hint">文本切块大小（字符），默认 500</span>
      </el-form-item>

      <el-form-item label="分块重叠" prop="chunk_overlap">
        <el-input-number v-model="form.chunk_overlap" :min="0" :step="10" />
        <span class="form-hint">相邻分块重叠长度，默认 50</span>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">
        {{ isEdit ? '保存' : '创建' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type {
  KnowledgeBaseCreate,
  KnowledgeBaseSimple,
  KnowledgeBaseUpdate,
  KnowledgeScope,
  OrganizationOut,
} from '@/types/knowledge'

const props = defineProps<{
  modelValue: boolean
  /** 编辑对象；为 null 时是创建模式 */
  kb?: KnowledgeBaseSimple | null
  organizations: OrganizationOut[]
  isAdmin: boolean
  submitting?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  submit: [payload: { id?: number; data: KnowledgeBaseCreate | KnowledgeBaseUpdate }]
}>()

const isEdit = computed(() => !!props.kb)

interface KBForm {
  name: string
  description: string
  scope: KnowledgeScope
  org_id: number | null
  chunk_size: number
  chunk_overlap: number
}

const formRef = ref<FormInstance>()
const form = reactive<KBForm>({
  name: '',
  description: '',
  scope: 'personal',
  org_id: null,
  chunk_size: 500,
  chunk_overlap: 50,
})

const rules: FormRules = {
  name: [
    { required: true, message: '请输入知识库名称', trigger: 'blur' },
    { max: 100, message: '名称不能超过 100 个字符', trigger: 'blur' },
  ],
}

// 打开弹窗时用编辑对象初始化表单
watch(
  () => [props.modelValue, props.kb] as const,
  ([open]) => {
    if (open) {
      if (props.kb) {
        form.name = props.kb.name
        form.description = props.kb.description || ''
        form.scope = props.kb.scope
        form.chunk_size = 500
        form.chunk_overlap = 50
      } else {
        form.name = ''
        form.description = ''
        form.scope = 'personal'
        form.org_id = null
        form.chunk_size = 500
        form.chunk_overlap = 50
      }
    }
  }
)

function handleClosed() {
  formRef.value?.clearValidate()
}

async function handleSubmit() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  if (isEdit.value && props.kb) {
    const data: KnowledgeBaseUpdate = {
      name: form.name.trim(),
      description: form.description.trim() || undefined,
      chunk_size: form.chunk_size,
      chunk_overlap: form.chunk_overlap,
    }
    emit('submit', { id: props.kb.id, data })
  } else {
    const data: KnowledgeBaseCreate = {
      name: form.name.trim(),
      description: form.description.trim() || null,
      scope: form.scope,
      chunk_size: form.chunk_size,
      chunk_overlap: form.chunk_overlap,
      org_id: form.scope === 'org' ? form.org_id : null,
    }
    emit('submit', { data })
  }
}
</script>

<style scoped>
.form-hint {
  font-size: var(--text-xs);
  color: var(--color-muted-foreground);
  margin-left: var(--space-3);
  line-height: 1.5;
}
</style>
