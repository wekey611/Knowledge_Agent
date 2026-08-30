# rag/interfaces/parser.py
"""
文档解析器接口定义。

为什么需要这个接口：
    文档格式有多种（PDF、DOCX、Markdown、TXT、HTML...），
    业务代码不应该知道具体格式。定义接口后，换解析器只改 factory.py。

职责边界（重要）：
    Parser 只负责"读文档 → 纯文本 + 元数据"。
    切块（chunker）是另一个独立模块（rag/chunker.py）的工作。
    Parser 不应承担切块职责，避免一个类做两件事。

修复历史：
    V0.1 依赖了 langchain_core.documents.Document。
    V0.2 定义自己的 ParsedDocument 数据结构，接口层零外部依赖。
    V0.2 移除 parse_to_documents（切块是独立模块的事）。
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Union


@dataclass
class ParsedDocument:
    """
    解析后的文档结构。

    Attributes:
        content: 纯文本内容
        metadata: 元数据（页数、作者、创建时间等）
        source: 来源标识（文件路径或 URL）
    """

    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: str = ""


class DocumentParserInterface(ABC):
    """
    文档解析器抽象接口。

    所有解析器实现（PDFParser、DocxParser、MarkdownParser 等）
    都必须继承此类。

    设计原则：每个 Parser 类只负责一种格式
        不要写一个 "UniversalParser" 能解析所有格式。
        应该 PDFParser 只解析 PDF，DocxParser 只解析 DOCX，
        用工厂（factory）按文件后缀分派。
    """

    # ==================== 核心方法（必须实现） ====================

    @abstractmethod
    def parse(self, source: Union[str, Path], **kwargs) -> ParsedDocument:
        """
        解析单个文档，返回纯文本 + 元数据。

        Args:
            source: 文件路径或 Path 对象
            **kwargs: 解析器特定参数（如 PDF 密码、页码范围等）

        Returns:
            ParsedDocument 对象

        Raises:
            FileNotFoundError: 文件不存在
            ParseError: 解析失败
            ValueError: 文件格式不支持

        Note:
            实现要点：
            - 只读出文本和元数据，不要切块
            - 元数据至少包含 file_extension（如 "pdf"）和 file_size
            - 失败时抛异常，不要返回空 ParsedDocument
        """
        raise NotImplementedError

    @abstractmethod
    def supports_format(self, file_extension: str) -> bool:
        """
        检查是否支持指定文件格式。

        Args:
            file_extension: 文件扩展名（不含点），如 "pdf" / "docx"

        Returns:
            True 表示支持
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def supported_formats(self) -> List[str]:
        """
        返回支持的格式扩展名列表。

        Returns:
            如 ["pdf"] / ["docx"] / ["md", "markdown"]
        """
        raise NotImplementedError