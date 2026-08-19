# Changelog

本项目变更记录，按日期倒序排列。格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [2026-08-14]

### 新增

- **知识库删除接口** `DELETE /knowledge-bases/{id}`：软删除（`deleted` 标记），仅知识库创建者可删
  - 配套测试 `tests/knowledgebase/test_delete.py`（10 个用例）
  - 查询层全部过滤已删除记录（`get_base` / `get_bases` / `count_personal` / `exists_by_name`）
- **文档上传接口** `POST /knowledge-bases/{kb_id}/documents`：
  - 本地磁盘存储（`StorageService`，按知识库分目录 + uuid 文件名）
  - 完整落库：`file_type` / `file_hash`(sha256) / `storage_key` / `parser_status=waiting`
- **文档列表 / 详情 / 下载 / 删除接口**（`/knowledge-bases/{kb_id}/documents...`）
  - 下载用 `FileResponse` 返回原文件，保留原始文件名
- **设计文档** `docs/document-upload-and-chunking-design.md`：上传存储与 RAG 切块的整体方案与决策记录

### 变更

- **文档权限方案 A 落地**：上传 / 删除仅限知识库创建者（`kb.owner_id == 当前用户`），读取按 scope 可见（personal 本人 / org 成员 / public 所有人）
- **文档不可变设计**：去掉 PATCH 修改接口，更新 = 重新上传新文档 + 删除旧文档
- `StorageService.base_path` 由实例属性改为**类属性**（支持测试注入临时目录）

### 修复

- `check_knowledge_base_access` / `check_knowledge_base_owner` 调用参数错位（service 层未传 `current_user` 导致运行时报错）
- `DocumentSimple` / `DocumentDetail` 缺失 `model_config = {"from_attributes": True}` 导致响应序列化失败；`file_hash` 改为可选
- `download` 引用不存在的 `document.file_path`（应为 `storage_key`）
- `check_knowledge_base_owner` 冗余查询与缺失的 404 处理
- 删除与 `get_detail` 完全重复的 `get_download` 方法
- **测试基建**：
  - `conftest.py` 新增 `ensure_test_users`（autouse）：保证 999999 测试用户存在，避免外键约束失败
  - `test_create_user.py` 幂等化：固定 `id=999999` 改为随机 id（重复运行不再主键冲突）
  - 新增 `tests/document/test_document.py`（21 个用例，含方案 A 权限正反验证）

### 待办

- 上传校验链：文件类型白名单、大小限制（方案文档中已规划）
- 文档列表分页
- 重复上传策略（同 `file_hash` 如何处理）
- 解析 + 切块流水线（阶段二）
