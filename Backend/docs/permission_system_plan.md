# 权限系统实现方案

## 背景

当前项目已有 Organization / OrganizationMember / KnowledgeBase / Document / Chunk 的模型定义，但存在以下问题需要先修复：
- Chunk 嵌套在 Document 类内部（SQLAlchemy 不会注册嵌套类，表建不出来）
- `models/__init__.py` 未导入 `knowledge`
- User 模型缺少 `organizations` / `organization_members` 的 relationship 引用
- 没有权限校验层和业务 API

目标：在现有代码上修复问题，并实现完整的组织 + 知识库权限体系。

---

## 功能模块切割

按可独立验证、可逐步上线的原则，拆分为 5 个阶段：

### 阶段一：模型修复

**目标：** 让 `alembic upgrade head` 能跑通，7 张表全部建成功。

| 文件 | 改动内容 |
|---|---|
| `models/knowledge.py` | Chunk 从 Document 内部提到模块顶层，修复缩进 |
| `models/user.py` | User 类追加 `organizations` 和 `organization_members` 两个 relationship |
| `models/__init__.py` | 加 `from . import knowledge` |
| `settings/__init__.py` | 新增配置 `PERSONAL_KB_LIMIT = 10` |

User 模型需要追加的两行（与已有的 relationship 同级）：
```python
organizations = relationship("Organization", back_populates="owner")
organization_members = relationship("OrganizationMember", back_populates="user")
```

**验证方法：** 跑 `alembic revision --autogenerate` + `alembic upgrade head`，确认所有表存在。

---

### 阶段二：权限基础设施

**目标：** 提供可复用的权限校验依赖，供后续阶段使用。

**新增：** `core/permissions.py`
- `visible_kb_filter(user_id, user_org_ids)` — 返回知识库列表的 SQLAlchemy where 条件
- 三合一查询：`scope=public` ∪ `scope=org AND org_id in user_org_ids` ∪ `scope=personal AND owner_id=user_id`

**改动：** `core/oauth2.py` — 新增两个 FastAPI 依赖函数
- `require_super_admin` — 检查 `current_user.role == admin`，用于保护公共库的写操作
- `require_org_admin(org_id)` — 查询 `OrganizationMember` 表，检查用户角色是否为 owner/admin

---

### 阶段三：组织管理 API

**目标：** 完整的组织 CRUD + 成员管理。

**新增文件：**

| 文件 | 核心内容 |
|---|---|
| `schemas/org.py` | OrganizationCreate, OrganizationOut, MemberAddIn, MemberOut |
| `repositories/org.py` | OrganizationRepository（CRUD + 成员数/用户组查询）, OrganizationMemberRepository |
| `routers/org.py` | 前缀 `/organizations`，9 个端点 |

**端点清单：**

| 方法 | 路径 | 权限 | 说明 |
|---|---|---|---|
| POST | `/organizations/` | 登录用户 | 创建（自动成为 OWNER） |
| GET | `/organizations/` | 登录用户 | 我的组织列表 |
| GET | `/organizations/{id}` | 组织成员 | 组织详情 |
| PATCH | `/organizations/{id}` | org_admin | 更新信息 |
| DELETE | `/organizations/{id}` | org_admin | 软删除 |
| GET | `/{id}/members` | 组织成员 | 成员列表 |
| POST | `/{id}/members` | org_admin | 添加成员 |
| PATCH | `/{id}/members/{uid}` | org_admin | 修改角色 |
| DELETE | `/{id}/members/{uid}` | org_admin | 移除成员 |

---

### 阶段四：知识库 API + 权限控制

**目标：** 带权限过滤的知识库 CRUD。

**新增文件：**

| 文件 | 核心内容 |
|---|---|
| `schemas/knowledge.py` | KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeBaseOut |
| `repositories/knowledge.py` | KnowledgeBaseRepository（含权限守卫函数） |
| `routers/knowledge.py` | 前缀 `/knowledge-bases`，5 个端点 |

**权限校验逻辑（写在 Repository 层）：**

- **读操作**：WHERE 条件 = 阶段二的 `visible_kb_filter`
- **写操作**：按 scope 分派
  - `personal` → 本人
  - `org` → 组织 admin/owner
  - `public` → 超级 admin
- **创建时额外校验**：
  - `scope=personal` → 当前用户 personal KB 数量 < `PERSONAL_KB_LIMIT`
  - `scope=org` → org_id 必填，且当前用户是该组织的 admin/owner
  - `scope=public` → 当前用户是 super admin

**端点清单：**

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/knowledge-bases/` | 当前用户可见的知识库列表 |
| GET | `/knowledge-bases/{id}` | 知识库详情 |
| POST | `/knowledge-bases/` | 创建（含权限和数量校验） |
| PATCH | `/knowledge-bases/{id}` | 更新 |
| DELETE | `/knowledge-bases/{id}` | 删除 |

---

### 阶段五：集成收尾

**目标：** 把所有模块串起来。

| 文件 | 改动 |
|---|---|
| `routers/__init__.py` | 加 `from . import org, knowledge` |
| `schemas/__init__.py` | 加 `from . import org, knowledge` |
| `main.py` | 加两行 `app.include_router(...)` |
| `admin.py` | 注册 OrganizationAdmin / KnowledgeBaseAdmin |

---

## 依赖关系

```
阶段一（模型修复） → 阶段二（权限基础设施） → 阶段三（组织 API）
                                                ↘ 阶段四（知识库 API）
                                                        ↘ 阶段五（集成收尾）
```

- 阶段二是阶段三/四的前置
- 阶段三和阶段四可并行开发（依赖同一份基础设施）
- 阶段五无新逻辑，只做配置

---

## 验证方案

1. **migration** — `alembic upgrade head` 确认 7 张表：`users` / `users_request` / `invite_tokens` / `organization` / `organization_member` / `knowledge_base` / `document` / `chunk`
2. **组织 API** — 创建组织 → 添加成员 → 修改角色 → 验证可见性
3. **知识库 API** — 不同用户角色创建 personal/org/public KB → 交叉验证可见列表
4. **权限边界** — 普通用户操作组织库应 403，非成员看不到组织库
5. **数量限制** — 创建 11 个 personal KB 时第 11 个应被拒绝
