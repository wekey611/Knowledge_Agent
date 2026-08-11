# Knowledge Agent Backend

知识管理系统后端服务，提供用户认证、注册审批、邮件通知、组织管理、知识库与文档管理等能力。

## 技术栈

| 组件 | 技术 |
|------|------|
| 框架 | FastAPI (~0.137) |
| 异步运行时 | Uvicorn / Starlette |
| 数据库 | MySQL 8.0+ (aiomysql 异步驱动) |
| ORM | SQLAlchemy 2.0 (异步) |
| 数据库迁移 | Alembic |
| 密码加密 | Argon2 (pwdlib) |
| JWT 认证 | python-jose (HS256) |
| 数据校验 | Pydantic v2 |
| 邮件发送 | fastapi-mail |
| 管理后台 | SQLAdmin |

## 快速开始

### 环境要求

- Python 3.12+
- MySQL 8.0+
- QQ 邮箱（用于发送邮件）

### 安装

```bash
# 克隆项目后，进入后端目录
cd Backend

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
source .venv/Scripts/activate
# Linux/Mac:
# source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install fastapi-mail
```

### 配置环境变量

复制并修改 `.env` 文件：

```ini
# 数据库连接
DB_URI = mysql+aiomysql://用户名:密码@127.0.0.1:3306/数据库名?charset=utf8mb4

# QQ 邮箱配置（用于发送注册邀请邮件）
MAIL_USERNAME=你的QQ邮箱@qq.com
MAIL_PASSWORD=QQ邮箱授权码（非登录密码）
MAIL_FROM=你的QQ邮箱@qq.com
MAIL_PORT=465
MAIL_SERVER=smtp.qq.com
MAIL_FROM_NAME=Knowledge_Agent
MAIL_STARTTLS=False
MAIL_SSL_TLS=True
```

> **QQ 邮箱授权码获取**：登录 QQ 邮箱 → 设置 → 账户 → POP3/IMAP/SMTP 服务 → 生成授权码

> **可选配置**（均有默认值，可不设置）：`PERSONAL_KB_LIMIT=10` 个人知识库数量上限；`MAX_FILE_SIZE=20971520` 文档大小上限（20MB）；`STORAGE_DIR` 文件存储根目录（默认 `Backend/storage`）。

### 初始化数据库

```bash
# 创建数据库（在 MySQL 中执行）
# CREATE DATABASE 数据库名 CHARACTER SET utf8mb4;

# 运行数据库迁移
alembic upgrade head
```

### 启动服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://127.0.0.1:8000 查看 API 健康状态。  
访问 http://127.0.0.1:8000/docs 查看 Swagger 文档。  
访问 http://127.0.0.1:8000/admin 进入 SQLAdmin 管理后台。

---

## 架构说明

```
app/
├── main.py              # 应用入口、路由注册、健康检查
├── admin.py             # SQLAdmin 管理后台视图
├── settings/            # 配置管理（从 .env 读取）
├── core/                # 基础设施层
│   ├── database.py      # 数据库引擎与会话管理
│   ├── security.py      # 密码哈希（Argon2）
│   ├── oauth2.py        # JWT 令牌生成/验证、当前用户依赖
│   ├── permissions.py   # 知识库可见性过滤与读写权限助手
│   ├── storage.py       # 文件存储（类型/大小校验、落盘、路径解析）
│   └── mail.py          # 邮件发送（fastapi-mail）
├── models/              # SQLAlchemy 数据模型
│   ├── user.py          # User / User_request / InviteToken
│   ├── auth.py          # Organization / OrganizationMember
│   └── knowledge.py     # KnowledgeBase / Document / Chunk
├── schemas/             # Pydantic 请求/响应模型
│   ├── user.py          # 用户相关 schema
│   ├── auth.py          # 认证相关 schema
│   ├── organization.py  # 组织相关 schema
│   └── knowledge.py     # 知识库/文档相关 schema
├── repositories/        # 数据访问层
│   ├── user.py          # 用户创建、登录、注册、token 查询
│   ├── request.py       # 申请提交、审批、查询
│   ├── organization.py  # 组织与成员管理
│   └── knowledge.py     # 知识库与文档 CRUD、上传
├── routers/             # API 路由
│   ├── user.py          # /user/* 用户相关端点
│   ├── auth.py          # /login、/admin/requests
│   ├── admin.py         # /admin/* 管理员端点
│   ├── organization.py  # /organization/* 组织相关端点
│   ├── knowledge.py     # /knowledge-bases/* 知识库与文档端点
│   └── document.py      # /documents/* 文档端点
├── services/            # 业务逻辑层（预留）
├── middleware/           # 中间件（预留）
└── static/              # 静态文件
    └── register.html    # 注册落地页
```

---

## API 文档

### 用户模块 `/user`

| 方法 | 路径 | 认证 | 说明 |
|------|------|:----:|------|
| POST | `/user/` | 否 | 直接注册（开放注册，绕过审批） |
| POST | `/user/request` | 否 | 提交注册申请（需管理员审批） |
| POST | `/user/register` | 否 | 通过邀请 token 完成注册 |
| GET | `/user/invite-info` | 否 | 查询邀请 token 信息（无副作用） |

**请求/响应示例：**

<details>
<summary><code>POST /user/request</code> — 提交申请</summary>

```json
// Request
{ "email": "user@example.com", "reason": "需要使用知识管理功能" }

// Response 201
{ "id": 1, "email": "user@example.com", "reason": "...", "status": "pending" }
```
</details>

<details>
<summary><code>GET /user/invite-info?token=xxx</code> — 查询 token</summary>

```json
// Response
{ "email": "user@example.com", "expired": false, "used": false }
```
</details>

<details>
<summary><code>POST /user/register</code> — 完成注册</summary>

```json
// Request
{ "token": "4yg40EV6SPMK...", "password": "your_password" }

// Response 201
{ "id": 1, "email": "user@example.com", "created_at": "2026-07-20T..." }
```
</details>

### 认证模块 `/login`

| 方法 | 路径 | 认证 | 说明 |
|------|------|:----:|------|
| POST | `/login` | 否 | 用户登录，返回 JWT（OAuth2 表单） |
| GET | `/admin/requests` | Admin | 列出所有注册申请 |

### 管理员模块 `/admin`

| 方法 | 路径 | 认证 | 说明 |
|------|------|:----:|------|
| POST | `/admin/{request_id}/approve` | Admin | 审批注册申请，发送邀请邮件 |

**请求示例：**

```bash
# 管理员登录获取 token
curl -X POST http://127.0.0.1:8000/login \
  -d "username=admin@example.com&password=admin123"

# 审批申请
curl -X POST http://127.0.0.1:8000/admin/1/approve \
  -H "Authorization: Bearer <jwt_token>"
```

### 知识库与文档模块 `/knowledge-bases` `/documents`

> 完整实现方案见 [`docs/knowledge_api_plan.md`](docs/knowledge_api_plan.md)。

**知识库：**

| 方法 | 路径 | 认证 | 说明 |
|------|------|:----:|------|
| GET | `/knowledge-bases` | 登录 | 当前用户可见的知识库列表 |
| POST | `/knowledge-bases` | 登录 | 创建知识库 |
| GET | `/knowledge-bases/{id}` | 登录 | 知识库详情 |
| PATCH | `/knowledge-bases/{id}` | 登录 | 更新知识库 |
| DELETE | `/knowledge-bases/{id}` | 登录 | 软删除知识库 |

**文档：**

| 方法 | 路径 | 认证 | 说明 |
|------|------|:----:|------|
| GET | `/knowledge-bases/{id}/documents` | 登录 | 知识库下文档列表 |
| POST | `/knowledge-bases/{id}/documents` | 登录 | 上传文档（multipart） |
| GET | `/documents/{id}` | 登录 | 文档详情 |
| PATCH | `/documents/{id}` | 登录 | 更新文档（标题/备注） |
| DELETE | `/documents/{id}` | 登录 | 软删除文档 |
| GET | `/documents/{id}/preview` | 登录 | 文档内联预览 |
| GET | `/documents/{id}/download` | 登录 | 文档下载 |

**响应字段为 camelCase**（对齐前端）：`documentCount`、`knowledgeBaseId`、`fileType`、`size`、`createdAt` 等。

**请求示例：**

```bash
# 创建知识库（scope: personal/org/public）
curl -X POST http://127.0.0.1:8000/knowledge-bases \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"产品文档","scope":"personal","chunkSize":500}'

# 上传文档（支持 pdf/docx/md/txt/html，默认最大 20MB）
curl -X POST http://127.0.0.1:8000/knowledge-bases/1/documents \
  -H "Authorization: Bearer <token>" \
  -F "file=@test.md" -F "title=测试文档"
```

**权限：** 知识库三种可见范围——`public` 公开 / `org` 组织内 / `personal` 个人；写操作按范围分级（个人库仅创建者、组织库组织管理员或创建者、公开库系统管理员）；个人知识库上限 10 个。

---

## 数据库模型

### User（用户）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 主键 |
| email | String(100), Unique | 邮箱 |
| password | String(200) | 密码（Argon2 哈希） |
| created_at | TIMESTAMP | 创建时间 |
| role | Enum("user", "admin") | 角色 |

### User_request（注册申请）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 主键 |
| email | String(100) | 申请人邮箱 |
| reason | String(1000) | 申请理由 |
| status | String(20) | pending / approved / registered / expired |

### InviteToken（邀请令牌）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 主键 |
| request_id | Integer FK → users_request.id | 关联申请单 |
| email | String(100) | 接收邀请的邮箱 |
| token_hash | String(255), Unique | SHA256 哈希的 token |
| expire_at | TIMESTAMP | 过期时间（3天） |
| used_at | TIMESTAMP, Nullable | 使用时间 |
| created_at | TIMESTAMP | 创建时间 |

### KnowledgeBase（知识库）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigInteger PK | 主键 |
| name | String(100) | 名称 |
| description | Text | 描述 |
| scope | Enum(public/org/personal) | 可见范围 |
| owner_id | BigInteger FK → users.id | 创建者 |
| org_id | BigInteger FK → organization.id, Nullable | 所属组织（个人库为空） |
| document_count / chunk_count | Integer | 文档数 / 分块数统计 |
| chunk_size / chunk_overlap | Integer | 分块大小(500) / 重叠(50) |
| status | Enum(active/provisioning/archived/failed) | 状态 |
| created_at / updated_at | TIMESTAMP | 创建 / 更新时间 |
| deleted | Boolean | 软删除标记 |

### Document（文档）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigInteger PK | 主键 |
| kb_id | BigInteger FK → knowledge_base.id | 所属知识库 |
| uploader_id | BigInteger FK → users.id | 上传者 |
| title / filename | String(255) | 标题 / 原始文件名 |
| file_type | String(20) | pdf/docx/md/txt/html |
| mime_type | String(100) | 媒体类型 |
| file_size | BigInteger | 文件大小（字节） |
| file_hash | String(64) | SHA-256 哈希 |
| page_count | Integer | 页数 |
| storage_key | String(500) | 存储路径（相对 STORAGE_DIR） |
| parser_status | Enum(waiting/parsing/embedding/completed/failed) | 解析状态 |
| chunk_count / parse_duration | Integer | 分块数 / 解析耗时(秒) |
| created_at / updated_at / deleted | TIMESTAMP / Boolean | 时间与软删标记 |

### Chunk（分块）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigInteger PK | 主键 |
| document_id | BigInteger FK → document.id | 所属文档 |
| chunk_index | Integer | 分块序号（从 0 开始） |
| content | Text | 分块内容 |
| token_count | Integer | Token 数量估算 |
| vector_id | String(255) | 向量库中的向量 ID |

---

## 认证与权限

### 注册审批流程

```
用户                后端                         邮箱
 │                   │                           │
 ├─POST /user/request─→ → 写入 users_request ──→→ 确认邮件
 │                   │                           │
 │  管理员审批        │                           │
 ├─POST /admin/{id}/approve
 │                   ├─ status = "approved"
 │                   ├─ 生成 token → invite_tokens
 │                   ├─ 返回 register_url ──────→→ 邀请链接邮件
 │                   │                           │
 ├─点开链接 ──→ 注册页面
 ├─输入密码 ──→ POST /user/register
 │                   ├─ 校验 token 有效性
 │                   ├─ 创建 User
 │                   ├─ used_at = now
 │                   └─ 返回用户信息
```

### JWT 认证

- 登录成功后返回 `access_token`（Bearer token）
- Token 有效期：30 分钟（可配置）
- 过期后需重新登录

### 角色控制

- `user` — 普通用户，默认角色
- `admin` — 管理员，可审批申请、查看所有申请

**知识库范围权限**（详见「知识库与文档模块」）：

| scope | 读 | 写 |
|-------|----|----|
| `public` | 所有人 | 系统管理员 |
| `org` | 组织成员 | 组织管理员或创建者 |
| `personal` | 仅创建者 | 仅创建者 |

---

## 邮件通知

| 场景 | 触发接口 | 内容 |
|------|---------|------|
| 申请提交确认 | `POST /user/request` | "您的注册申请已提交，请等待管理员审核。" |
| 审批通过 | `POST /admin/{id}/approve` | 包含注册链接，有效期 3 天 |

当前使用 QQ 邮箱 SMTP 发送，支持配置其他邮箱。

---

## 数据库迁移

```bash
# 生成新迁移
alembic revision --autogenerate -m "描述"

# 应用到最新
alembic upgrade head

# 回退
alembic downgrade -1

# 查看历史
alembic history
```

---

## 开发指南

### 项目约定

- **Repository 模式**：数据库操作统一放在 `repositories/`，不在路由层直接操作数据库
- **异步优先**：所有数据库操作使用 async/await
- **依赖注入**：依赖通过 FastAPI `Depends` 注入
- **敏感信息**：`SECRET_KEY` 等敏感信息不要硬编码，放在 `.env`

### 代码分层

```
路由层 (routers/) → 仓库层 (repositories/) → 数据模型 (models/)
    │                     │
    │             基础设施 (core/)
    │             ├── database.py  (DB 连接)
    │             ├── security.py  (密码)
    │             ├── oauth2.py    (JWT)
    │             └── mail.py      (邮件)
    │
   层间通过 schema (Pydantic 模型) 传递数据
```
