// ========================================
// Chat — Mock API
// 后端尚未开发 RAG 聊天接口，前端暂用模拟数据
// ========================================
import type { ChatMessage } from '@/types/knowledge'

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

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

export async function fetchMessages(kbId: number): Promise<ChatMessage[]> {
  await delay(600)
  return mockMessages.filter((m) => m.knowledgeBaseId === kbId)
}

export async function sendMessage(kbId: number, content: string): Promise<ChatMessage> {
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
