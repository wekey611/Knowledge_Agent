"""
纯文本解析器。

支持：.txt 文件
"""
from pathlib import Path
from typing import Union

from rag.interfaces.parser import DocumentParserInterface, ParsedDocument


class TextParser(DocumentParserInterface):
    """
    纯文本解析器。

    直接读取文件内容，不做格式转换。
    """

    SUPPORTED_FORMATS = ["txt"]

    def parse(self, source: Union[str, Path], **kwargs) -> ParsedDocument:
        source = Path(source)
        if not source.exists():
            raise FileNotFoundError(f"文件不存在: {source}")

        # 尝试多种编码（中文文件常见 GBK）
        encodings = ["utf-8", "gbk", "gb2312", "latin-1"]
        content = None
        last_error = None

        for encoding in encodings:
            try:
                content = source.read_text(encoding=encoding)
                break
            except UnicodeDecodeError as e:
                last_error = e

        if content is None:
            raise ValueError(f"无法解码文件 {source}: {last_error}")

        return ParsedDocument(
            content=content,
            metadata={
                "file_extension": "txt",
                "file_size": source.stat().st_size,
            },
            source=str(source),
        )

    def supports_format(self, file_extension: str) -> bool:
        return file_extension.lower() in self.SUPPORTED_FORMATS

    @property
    def supported_formats(self) -> list:
        return self.SUPPORTED_FORMATS


__all__ = ["TextParser"]