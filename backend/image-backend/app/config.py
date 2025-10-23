import os
from typing import Set

class Settings:
    # 应用配置
    APP_NAME: str = "PCB缺陷检测API"
    VERSION: str = "1.0.0"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 文件配置
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 20 * 1024 * 1024  # 20MB
    ALLOWED_EXTENSIONS: Set[str] = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    
    # 算法配置
    DEFAULT_MODEL: str = "256"
    SIMULATE_PROCESSING_TIME: float = 2.0  # 模拟处理时间（秒）
    # ONNX 模型路径（根据实际模型文件位置调整）
    ONNX_MODEL_PATH: str = "app/models/20251005100417.onnx"

settings = Settings()