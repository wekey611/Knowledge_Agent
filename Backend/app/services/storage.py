# 存储文件的功能
from pathlib import Path
from uuid import uuid4


class StorageService:
    # 类属性：存储根目录，测试可 monkeypatch 注入临时目录
    base_path = Path("storage/knowledge_bases")

    async def save(
            self,
            kb_id:int,
            filename:str,
            content:bytes,
    )->str:
        kb_path = self.base_path / str(kb_id)
        kb_path.mkdir(
            parents=True,
            exist_ok=True,
        )
        extension =Path(filename).suffix

        stored_name = f"{uuid4().hex}{extension}"

        file_path = kb_path/stored_name

        file_path.write_bytes(content)

        return str(file_path)

    async def delete(self, key: str):
        """删除存储中的文件（不存在则静默通过，便于幂等清理）"""
        path = Path(key)
        if path.exists():
            path.unlink()