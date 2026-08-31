"""
RAGAS 0.2 + 新版 langchain-community 的兼容性补丁。

背景：
    RAGAS 0.2 在 ragas/llms/base.py:8 直接 import：
        from langchain_community.chat_models.vertexai import ChatVertexAI
    但新版 langchain-community 把 vertexai 子模块移走了，导致 import 直接报错。

解决方案：
    用 sys.modules stub 一个 dummy 模块绕过，让 RAGAS 以为这个 import 成功了。
    我们只用 RAGAS 的指标（不调 ChatVertexAI），所以 dummy 是安全的。

用法：
    在任何使用 RAGAS 的脚本最开头：
        from rag.evaluation.ragas_compat import apply_compat_patches
        apply_compat_patches()

    然后再 import ragas。

原理：
    sys.modules 是 Python 的模块缓存表。import 语句本质是查 sys.modules，
    找不到才执行模块文件。我们提前塞一个空模块进去，import 就直接成功。
"""
import sys
import types
from typing import List


def _make_stub_module(name: str, attrs: List[str]) -> types.ModuleType:
    """
    创建一个 dummy 模块对象，包含指定属性。
    类属性设为最简单的 type('Name', (), {})，满足 isinstance 检查。
    """
    module = types.ModuleType(name)
    for attr in attrs:
        setattr(module, attr, type(attr, (), {}))
    return module


# RAGAS 0.2 base.py 缺失的模块列表
_STUBS = [
    ("langchain_community.chat_models.vertexai", ["ChatVertexAI"]),
    ("langchain_community.llms", ["VertexAI"]),
    # 兜底：有些 ragas 子模块还会触发这两个
    ("langchain_community.embeddings.vertexai", ["VertexAIEmbeddings"]),
]


def apply_compat_patches() -> None:
    """
    应用所有兼容性 stub。幂等：重复调用安全。

    只 stub 缺失的（已存在的不会覆盖，避免破坏正常使用）。
    """
    for module_name, attrs in _STUBS:
        if module_name not in sys.modules:
            sys.modules[module_name] = _make_stub_module(module_name, attrs)


__all__ = ["apply_compat_patches"]