import os
import aiofiles
from fastapi import UploadFile, HTTPException
from app.config import settings

async def validate_image_file(file: UploadFile):
    """验证图片文件"""
    if not file.content_type or not file.content_type.startswith('image/'):
        raise ValueError("文件必须是图片格式")
    
    if file.size > settings.MAX_FILE_SIZE:
        raise ValueError(f"文件大小不能超过 {settings.MAX_FILE_SIZE // 1024 // 1024}MB")
    
    filename = file.filename.lower()
    file_ext = os.path.splitext(filename)[1]
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise ValueError(f"不支持的文件格式。支持的格式: {', '.join(settings.ALLOWED_EXTENSIONS)}")

async def save_upload_file(file: UploadFile, save_dir: str, filename: str = None) -> str:
    """保存上传的文件"""
    os.makedirs(save_dir, exist_ok=True)
    
    if not filename:
        import uuid
        file_ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{file_ext}"
    
    file_path = os.path.join(save_dir, filename)
    
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    return file_path

def ensure_directories():
    """确保必要的目录存在"""
    directories = [
        settings.UPLOAD_DIR,
        os.path.join(settings.UPLOAD_DIR, "original"),
        os.path.join(settings.UPLOAD_DIR, "processed"),
        os.path.join(settings.UPLOAD_DIR, "temp")
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)