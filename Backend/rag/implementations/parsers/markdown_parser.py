"""
Markdown 解析器。

支持：.md / .markdown 文件

为什么不剥离 Markdown 语法：
    V1 简化版：直接把整个 Markdown 内容当纯文本。
    原因：很多 RAG 场景保留 Markdown 结构反而有用（标题、列表对 LLM 是有用的格式提示）。
    V2 优化版：可用 unstructured 库提取结构化内容（标题层级、表格、列表等）。
"""
from pathlib import Path
from typing import Union

from rag.interfaces.parser import DocumentParserInterface, ParsedDocument
from rag.implementations.parsers.text_parser import TextParser


class MarkdownParser(DocumentParserInterface):
    """
    Markdown 解析器。

    实际上是对 TextParser 的简单包装（Markdown 本质是文本）。
    单独成一个类是为了：
        1. 未来可重写 parse() 用专业库（unstructured、markdown-it-py）
        2. metadata 可标记 file_extension=md（便于后续按格式过滤）
    """

    SUPPORTED_FORMATS = ["md", "markdown"]

    def __init__(self):
        self._text_parser = TextParser()

    def parse(self, source: Union[str, Path], **kwargs) -> ParsedDocument:
        parsed = self._text_parser.parse(source, **kwargs)
        # 改写 file_extension
        parsed.metadata["file_extension"] = "md"
        return parsed

    def supports_format(self, file_extension: str) -> bool:
        return file_extension.lower() in self.SUPPORTED_FORMATS

    @property
    def supported_formats(self) -> list:
        return self.SUPPORTED_FORMATS


__all__ = ["MarkdownParser"]