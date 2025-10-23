from fastapi import APIRouter
from app.utils.test_utils import TestImageGenerator
from app.services.base64_service import base64_service
import json

router = APIRouter(prefix="/api/test", tags=["testing"])

@router.get("/generate-test-data")
async def generate_test_data():
    """
    生成测试数据
    
    返回一对测试图片的Base64编码，可用于测试 /api/process 接口
    """
    try:
        # 生成测试图片
        query_image, gerber_image = TestImageGenerator.generate_test_images()
        
        # 转换为Base64
        query_b64 = base64_service.image_to_base64(query_image)
        gerber_b64 = base64_service.image_to_base64(gerber_image)
        
        # 构建测试请求数据
        test_request = {
            "queryImage": query_b64,
            "gerberImage": gerber_b64,
            "model": "256"
        }
        
        return {
            "message": "测试数据生成成功",
            "testRequest": test_request,
            "usage": "复制 testRequest 的内容到 /api/process 接口进行测试"
        }
        
    except Exception as e:
        return {"error": f"生成测试数据失败: {str(e)}"}