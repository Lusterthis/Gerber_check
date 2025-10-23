from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from app.models.schemas import ProcessRequest, ProcessResponse, ErrorResponse
from app.services.image_service import image_service
from app.services.base64_service import base64_service
import base64

router = APIRouter(prefix="/api", tags=["processing"])

@router.post(
    "/process",
    response_model=ProcessResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def process_images(request: ProcessRequest):
    """
    处理PCB图片并返回缺陷检测结果（Base64格式）
    
    - **queryImage**: 查询图片的Base64编码 (data:image/...)
    - **gerberImage**: Gerber图片的Base64编码 (data:image/...)  
    - **model**: 使用的模型版本 (默认: "256")
    """
    try:
        # 调用图片处理服务
        result = await image_service.process_pcb_images(
            query_image_b64=request.queryImage,
            gerber_image_b64=request.gerberImage,
            model=request.model
        )
        
        return result
        
    except ValueError as e:
        # 客户端错误（如Base64解析失败）
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error="请求数据格式错误",
                detail=str(e)
            ).dict()
        )
    except Exception as e:
        # 服务器错误
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="图片处理失败",
                detail=str(e)
            ).dict()
        )

@router.post(
    "/process-upload",
    response_model=ProcessResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def process_upload_images(
    files: list[UploadFile] = File(..., description="请依次上传两张图片：第一张为查询图片，第二张为Gerber图片"),
    model: str = Form("256", description="模型版本")
):
    """
    通过文件上传处理PCB图片（测试用）
    
    这个接口允许通过表单上传两张图片文件进行测试，更适合浏览器测试。
    注意：请按顺序上传两张图片，第一张为查询图片，第二张为Gerber图片。
    """
    try:
        # 验证文件数量
        if len(files) != 2:
            raise ValueError("请上传两张图片：第一张为查询图片，第二张为Gerber图片")
        
        query_image = files[0]
        gerber_image = files[1]
        
        # 验证文件类型
        if not query_image.content_type.startswith('image/') or not gerber_image.content_type.startswith('image/'):
            raise ValueError("请上传图片文件")
        
        # 读取图片文件并转换为Base64
        query_content = await query_image.read()
        gerber_content = await gerber_image.read()
        
        # 转换为Base64 Data URL格式
        query_b64 = f"data:{query_image.content_type};base64,{base64.b64encode(query_content).decode('utf-8')}"
        gerber_b64 = f"data:{gerber_image.content_type};base64,{base64.b64encode(gerber_content).decode('utf-8')}"
        
        # 调用图片处理服务
        result = await image_service.process_pcb_images(
            query_image_b64=query_b64,
            gerber_image_b64=gerber_b64,
            model=model
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error="文件格式错误",
                detail=str(e)
            ).dict()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="图片处理失败",
                detail=str(e)
            ).dict()
        )
@router.get("/test-images")
async def get_test_images():
    """
    获取测试图片信息（用于开发测试）
    """
    import os
    test_dir = "test_images"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
        return {
            "message": "测试图片目录已创建，请放置测试图片",
            "directory": test_dir,
            "suggested_files": ["query.png", "gerber.png"]
        }
    
    files = os.listdir(test_dir)
    return {
        "available_test_images": files,
        "usage": "使用 /api/process-test 接口进行测试"
    }

@router.post(
    "/process-test",
    response_model=ProcessResponse
)
async def process_test_images(model: str = Form("256")):
    """
    使用测试目录中的图片进行处理（开发测试用）
    """
    try:
        import os
        test_dir = "test_images"
        
        # 检查测试图片是否存在
        query_path = os.path.join(test_dir, "query.png")
        gerber_path = os.path.join(test_dir, "gerber.png")
        
        if not os.path.exists(query_path):
            query_path = os.path.join(test_dir, "query.jpg")
        if not os.path.exists(gerber_path):
            gerber_path = os.path.join(test_dir, "gerber.jpg")
        
        if not os.path.exists(query_path) or not os.path.exists(gerber_path):
            available_files = os.listdir(test_dir) if os.path.exists(test_dir) else []
            raise ValueError(f"测试图片不存在。请将query.png和gerber.png放入{test_dir}目录。现有文件: {available_files}")
        
        # 读取图片文件
        with open(query_path, "rb") as f:
            query_content = f.read()
        with open(gerber_path, "rb") as f:
            gerber_content = f.read()
        
        # 转换为Base64
        query_b64 = f"data:image/png;base64,{base64.b64encode(query_content).decode('utf-8')}"
        gerber_b64 = f"data:image/png;base64,{base64.b64encode(gerber_content).decode('utf-8')}"
        
        # 调用处理服务
        result = await image_service.process_pcb_images(
            query_image_b64=query_b64,
            gerber_image_b64=gerber_b64,
            model=model
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="测试处理失败",
                detail=str(e)
            ).dict()
        )