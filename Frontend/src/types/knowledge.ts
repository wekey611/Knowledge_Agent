// ========================================
// Knowledge Base — Type Definitions
// 字段与后端 FastAPI schemas 对齐（snake_case）
// ========================================

// === 知识库 ===

export type KnowledgeScope = 'public' | 'org' | 'personal'
export type KBStatus = 'active' | 'provisioning' | 'archived' | 'failed'

/** 列表项（KnowledgeBaseSimple） */
export interface KnowledgeBaseSimple {
  id: number
  name: string
  description: string | null
  scope: KnowledgeScope
  status: KBStatus
  document_count: number
  created_at: string
}

/** 详情（KnowledgeBaseDetail） */
export interface KnowledgeBase extends KnowledgeBaseSimple {
  chunk_count: number
  chunk_size: number
  chunk_overlap: number
  owner_id: number
  org_id: number | null
  organization: OrganizationOut | null
  updated_at: string
}

export interface KnowledgeBaseList {
  total: number
  data: KnowledgeBaseSimple[]
}

export interface KnowledgeBaseCreate {
  name: string
  description?: string | null
  scope: KnowledgeScope
  chunk_size?: number
  chunk_overlap?: number
  org_id?: number | null
}

export interface KnowledgeBaseUpdate {
  name?: string
  description?: string
  chunk_size?: number
  chunk_overlap?: number
}

// === 组织 ===

export type OrgRole = 'owner' | 'admin' | 'member'

/** OrganizationOut（知识库详情中的 organization 字段） */
export interface OrganizationOut {
  id: number
  name: string
  description: string
  created_at: string
}

export interface OrgMemberUser {
  id: number
  username: string
  email: string
}

/** OrganizationMemberOut */
export interface OrganizationMember {
  role: OrgRole
  joined_at: string
  user: OrgMemberUser | null
}

/** OrganizationDetail */
export interface Organization extends OrganizationOut {
  owner: OrgMemberUser | null
  members: OrganizationMember[] | null
}

export interface OrganizationCreate {
  name: string
  description: string
}

export interface OrganizationUpdate {
  name: string
  description: string
}

// === 文档 / 聊天（后端尚未开发，保留 mock 用） ===

export interface Document {
  id: number
  knowledgeBaseId: number
  title: string
  fileType: string
  size: number
  parentId: number | null
  createdAt: string
}

export interface ChatMessage {
  id: string
  knowledgeBaseId: number
  role: 'user' | 'assistant'
  content: string
  sources?: SourceReference[]
  createdAt: string
  status: 'sending' | 'sent' | 'error'
}

export interface SourceReference {
  documentId: number
  documentTitle: string
  snippet: string
  score: number
}

export interface DocumentTreeNode {
  id: number
  label: string
  type: 'folder' | 'file'
  fileType?: string
  children?: DocumentTreeNode[]
}

// === 展示辅助 ===

export const SCOPE_LABELS: Record<KnowledgeScope, string> = {
  personal: '个人',
  org: '组织',
  public: '公开',
}

export const SCOPE_COLORS: Record<KnowledgeScope, string> = {
  personal: '#2563EB',
  org: '#6366F1',
  public: '#06B6D4',
}

export const KB_STATUS_LABELS: Record<KBStatus, string> = {
  active: '正常',
  provisioning: '初始化中',
  archived: '已归档',
  failed: '异常',
}

export const ORG_ROLE_LABELS: Record<OrgRole, string> = {
  owner: '所有者',
  admin: '管理员',
  member: '成员',
}

/** 角色标签的安全取值（处理 null/任意字符串） */
export function orgRoleLabel(role: string | null | undefined): string {
  if (!role) return '未知'
  return ORG_ROLE_LABELS[role as OrgRole] || role
}
