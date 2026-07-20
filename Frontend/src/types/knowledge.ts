// ========================================
// Knowledge Base — Type Definitions
// ========================================

export interface KnowledgeBase {
  id: number
  name: string
  description: string
  documentCount: number
  createdAt: string
  updatedAt: string
  color?: string
}

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
