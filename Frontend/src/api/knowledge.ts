// ========================================
// Knowledge Base API
// Mock data + HTTP fallback pattern
// ========================================
import type { KnowledgeBase, ChatMessage, Document } from '@/types/knowledge'
import http from './http'

// Toggle mock mode: true in dev, false in production
const USE_MOCK = true

// Helper for simulated network delay
function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

// ========================================
// Mock Data
// ========================================
const mockKnowledgeBases: KnowledgeBase[] = [
  {
    id: 1,
    name: '产品文档',
    description: '包含产品规格、用户手册和常见问题解答',
    documentCount: 24,
    createdAt: '2026-06-01T00:00:00Z',
    updatedAt: '2026-07-15T00:00:00Z',
    color: '#2563EB',
  },
  {
    id: 2,
    name: '技术手册',
    description: '系统架构设计、API 文档和开发指南',
    documentCount: 18,
    createdAt: '2026-06-10T00:00:00Z',
    updatedAt: '2026-07-18T00:00:00Z',
    color: '#7C3AED',
  },
  {
    id: 3,
    name: '市场分析',
    description: '行业研究报告、竞品分析和市场趋势预测',
    documentCount: 7,
    createdAt: '2026-07-01T00:00:00Z',
    updatedAt: '2026-07-20T00:00:00Z',
    color: '#10B981',
  },
]

const mockDocuments: Document[] = [
  { id: 1, knowledgeBaseId: 1, title: '产品规格说明书 v2.1', fileType: 'pdf', size: 2048, parentId: null, createdAt: '2026-06-01T00:00:00Z' },
  { id: 2, knowledgeBaseId: 1, title: '用户操作手册', fileType: 'pdf', size: 5120, parentId: null, createdAt: '2026-06-05T00:00:00Z' },
  { id: 3, knowledgeBaseId: 1, title: '常见问题 FAQ', fileType: 'md', size: 256, parentId: null, createdAt: '2026-06-10T00:00:00Z' },
  { id: 4, knowledgeBaseId: 1, title: 'API 参考文档', fileType: 'html', size: 1024, parentId: null, createdAt: '2026-06-15T00:00:00Z' },
  { id: 5, knowledgeBaseId: 2, title: '系统架构概览', fileType: 'pdf', size: 3072, parentId: null, createdAt: '2026-06-10T00:00:00Z' },
  { id: 6, knowledgeBaseId: 2, title: '数据库设计文档', fileType: 'md', size: 1536, parentId: null, createdAt: '2026-06-15T00:00:00Z' },
  { id: 7, knowledgeBaseId: 2, title: '部署指南', fileType: 'md', size: 768, parentId: null, createdAt: '2026-06-20T00:00:00Z' },
  { id: 8, knowledgeBaseId: 3, title: '2026 Q2 行业报告', fileType: 'pdf', size: 8192, parentId: null, createdAt: '2026-07-01T00:00:00Z' },
  { id: 9, knowledgeBaseId: 3, title: '竞品分析矩阵', fileType: 'xlsx', size: 512, parentId: null, createdAt: '2026-07-05T00:00:00Z' },
]

const mockMessages: ChatMessage[] = [
  {
    id: '1',
    knowledgeBaseId: 1,
    role: 'user',
    content: '请问产品的系统要求是什么？',
    createdAt: '2026-07-20T10:00:00Z',
    status: 'sent',
  },
  {
    id: '2',
    knowledgeBaseId: 1,
    role: 'assistant',
    content: '根据产品规格说明书 v2.1，系统要求如下：\n\n- 操作系统：Windows 10/11、macOS 12+、Ubuntu 20.04+\n- 内存：最低 8GB，推荐 16GB\n- 存储空间：至少 10GB 可用空间\n- 网络：稳定的互联网连接\n- 浏览器：Chrome 90+、Firefox 88+、Edge 90+',
    sources: [
      { documentId: 1, documentTitle: '产品规格说明书 v2.1', snippet: '系统要求...', score: 0.95 },
    ],
    createdAt: '2026-07-20T10:00:05Z',
    status: 'sent',
  },
  {
    id: '3',
    knowledgeBaseId: 1,
    role: 'user',
    content: '如何重置用户密码？',
    createdAt: '2026-07-20T10:05:00Z',
    status: 'sent',
  },
  {
    id: '4',
    knowledgeBaseId: 1,
    role: 'assistant',
    content: '重置用户密码的步骤：\n\n1. 打开登录页面，点击"忘记密码"链接\n2. 输入注册时使用的邮箱地址\n3. 检查收件箱，找到密码重置邮件\n4. 点击邮件中的重置链接\n5. 输入新密码并确认\n6. 密码重置成功后，使用新密码登录\n\n如果未收到重置邮件，请检查垃圾邮件箱或联系管理员。',
    sources: [
      { documentId: 2, documentTitle: '用户操作手册', snippet: '密码重置...', score: 0.92 },
    ],
    createdAt: '2026-07-20T10:05:03Z',
    status: 'sent',
  },
]

// ========================================
// API Functions
// ========================================

export async function fetchKnowledgeBases(): Promise<KnowledgeBase[]> {
  if (USE_MOCK) {
    await delay(800)
    return [...mockKnowledgeBases]
  }
  const res = await http.get<KnowledgeBase[]>('/knowledge-bases')
  return res.data
}

export async function fetchDocuments(kbId: number): Promise<Document[]> {
  if (USE_MOCK) {
    await delay(500)
    return mockDocuments.filter((d) => d.knowledgeBaseId === kbId)
  }
  const res = await http.get<Document[]>(`/knowledge/${kbId}/documents`)
  return res.data
}

export async function fetchMessages(kbId: number): Promise<ChatMessage[]> {
  if (USE_MOCK) {
    await delay(600)
    return mockMessages.filter((m) => m.knowledgeBaseId === kbId)
  }
  const res = await http.get<ChatMessage[]>(`/knowledge/${kbId}/messages`)
  return res.data
}

export async function sendMessage(kbId: number, content: string): Promise<ChatMessage> {
  if (USE_MOCK) {
    await delay(1200)
    return {
      id: `msg-${Date.now()}`,
      knowledgeBaseId: kbId,
      role: 'assistant',
      content: `这是对"${content}"的模拟回答。当后端 API 就绪后，这里将返回基于知识库内容的真实回答。\n\n你可以尝试询问关于产品规格、用户手册或常见问题等内容。`,
      createdAt: new Date().toISOString(),
      status: 'sent',
    }
  }
  const res = await http.post<ChatMessage>(`/knowledge/${kbId}/chat`, { content })
  return res.data
}
