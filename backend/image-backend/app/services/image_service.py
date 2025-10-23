from app.services.algorithm_service import algorithm_service
from app.services.base64_service import base64_service
from app.models.schemas import ProcessResponse
from PIL import Image
import traceback
from fastapi import UploadFile

class ImageService:
    """图片处理服务"""
    
    def __init__(self):
        self.algorithm_service = algorithm_service
        self.base64_service = base64_service
    
    async def process_pcb_images(self, query_image_b64: str, gerber_image_b64: str, model: str = "256") -> ProcessResponse:
        """
        处理PCB图片的主流程（Base64版本）
        """
        try:
            # 1. Base64解码
            query_image = self.base64_service.base64_to_image(query_image_b64)
            gerber_image = self.base64_service.base64_to_image(gerber_image_b64)
            
            # 2. 调用算法服务处理
            result = self.algorithm_service.process_images(query_image, gerber_image, model)
            
            # 3. 结果编码为Base64
            converted_gerber_b64 = self.base64_service.image_to_base64(result["converted_image"])
            anomaly_image_b64 = self.base64_service.image_to_base64(result["anomaly_image"])
            
            # 4. 构建响应
            return ProcessResponse(
                convertedGerber=converted_gerber_b64,
                anomalyImage=anomaly_image_b64,
                anomalyScore=result["anomaly_score"],
                defectDescription=result["defect_description"]
            )
            
        except Exception as e:
            print(f"图片处理失败: {str(e)}")
            print(traceback.format_exc())
            raise
    
    async def process_pcb_files(self, query_file: UploadFile, gerber_file: UploadFile, model: str = "256") -> ProcessResponse:
        """
        处理PCB图片的主流程（文件上传版本）
        """
        try:
            print(f"开始处理文件: {query_file.filename}, {gerber_file.filename}")
            
            # 1. 文件转换为Base64
            query_image_b64 = await self.base64_service.file_to_base64(query_file)
            gerber_image_b64 = await self.base64_service.file_to_base64(gerber_file)
            
            print("文件已转换为Base64")
            
            # 2. 调用Base64版本的处理流程
            return await self.process_pcb_images(query_image_b64, gerber_image_b64, model)
            
        except Exception as e:
            print(f"文件处理失败: {str(e)}")
            print(traceback.format_exc())
            raise

# 创建全局服务实例
image_service = ImageService()