# 存储文件的功能
from pathlib import Path
from uuid import uuid4


class StorageService:
    def __init__(self):
        self.base_path = Path("storage/knowledge_bases")

    async def save(
            self,
            kb_id:int,
            filename:str,
            content:bytes,
    )->str:
        kb_path =self.base_path/str(kb_id)
        kb_path.mkdir(
            parents=True,
            exist_ok=True,
        )
        extension =Path(filename).suffix

        stored_name = f"{uuid4().hex}{extension}"

        file_path = kb_path/stored_name

        file_path.write_bytes(content)

        return str(file_path)