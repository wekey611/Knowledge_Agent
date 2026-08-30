"""
PDF 解析器。

使用 pypdf 库（纯 Python，无系统依赖）。

依赖：
    pip install pypdf

能力：
    - 提文本（每页加页码标记 [Page N]，便于溯源）
    - 支持加密 PDF（需传入 password 参数）
    - metadata 包含页数、文件大小

不擅长（V5 再加）：
    - 扫描件 PDF（需要 OCR，如 pytesseract）
    - 复杂表格提取（需要 pdfplumber）
    - 图片提取（需要 pdf2image）

依赖：
    pip install pypdf
"""
from pathlib import Path
from typing import Optional, Union

from rag.interfaces.parser import DocumentParserInterface, ParsedDocument


class PDFParser(DocumentParserInterface):
    """
    PDF 解析器。

    Attributes:
        page_separator: 页与页之间的分隔符，默认 "\n\n"
    """

    SUPPORTED_FORMATS = ["pdf"]

    def __init__(self, page_separator: str = "\n\n"):
        self.page_separator = page_separator

    def parse(self, source: Union[str, Path], **kwargs) -> ParsedDocument:
        """
        解析 PDF 为纯文本。

        Args:
            source: PDF 文件路径
            **kwargs:
                - password: PDF 密码（加密时必填）

        Returns:
            ParsedDocument，content 是"页码+文本"格式
        """
        # 延迟导入（避免 pypdf 没装时整个 rag 模块崩溃）
        try:
            import pypdf
        except ImportError:
            raise ImportError(
                "PDFParser 需要 pypdf 库，请先安装：pip install pypdf"
            )

        source = Path(source)
        if not source.exists():
            raise FileNotFoundError(f"文件不存在: {source}")

        password = kwargs.get("password")
        try:
            reader = pypdf.PdfReader(str(source))
        except Exception as e:
            raise ValueError(f"无法读取 PDF {source}: {e}")

        # 处理加密 PDF
        if reader.is_encrypted:
            if not password:
                raise ValueError(
                    f"PDF {source} 已加密，需提供 password 参数"
                )
            decrypt_result = reader.decrypt(password)
            if not decrypt_result:
                raise ValueError(f"PDF 密码错误: {source}")

        # 逐页提取文本
        pages_text = []
        for i, page in enumerate(reader.pages):
            try:
                text = page.extract_text() or ""
            except Exception as e:
                # 单页提取失败不影响整体
                text = f"[Page {i+1} 提取失败: {e}]"

            # 加页码标记，便于溯源
            pages_text.append(f"[Page {i+1}]\n{text}")

        content = self.page_separator.join(pages_text)

        return ParsedDocument(
            content=content,
            metadata={
                "file_extension": "pdf",
                "page_count": len(reader.pages),
                "file_size": source.stat().st_size,
            },
            source=str(source),
        )

    def supports_format(self, file_extension: str) -> bool:
        return file_extension.lower() in self.SUPPORTED_FORMATS

    @property
    def supported_formats(self) -> list:
        return self.SUPPORTED_FORMATS


__all__ = ["PDFParser"]