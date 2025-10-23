from pydantic import BaseModel
from typing import Optional

class ProcessRequest(BaseModel):
    queryImage: str  # Base64编码的查询图片
    gerberImage: str  # Base64编码的Gerber图片
    model: str = "256"  # 模型参数，默认值256

class ProcessResponse(BaseModel):
    convertedGerber: str  # Base64编码的处理后Gerber图片
    anomalyImage: str  # Base64编码的异常图片
    anomalyScore: float  # 异常分数 0-1
    defectDescription: str  # 缺陷描述