import sys
import os
import uuid

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.config import settings
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.services.image_service import image_service
from app.models.schemas import ProcessResponse
import uvicorn
from app.services.onnx_service import onnx_service

# 临时导入解决方案（如果file_utils还没创建）
async def validate_image_file(file: UploadFile):
    """临时的文件验证函数"""
    if not file.content_type or not file.content_type.startswith('image/'):
        raise ValueError("文件必须是图片格式")

    # 计算文件大小（UploadFile 无 .size 属性）
    content = await file.read()
    file_size = len(content)
    if file_size > 10 * 1024 * 1024:  # 10MB
        raise ValueError("文件大小不能超过10MB")

    # 重置读取指针，后续流程还需要读取内容
    file.file.seek(0)

    filename = file.filename.lower()
    if not any(filename.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp']):
        raise ValueError("不支持的文件格式")

async def save_upload_file(file: UploadFile, save_dir: str, filename: str) -> str:
    """临时的文件保存函数"""
    import aiofiles
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, filename)
    
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    return file_path

# 确保上传目录存在
os.makedirs("uploads/original", exist_ok=True)
os.makedirs("uploads/processed", exist_ok=True)

app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

# 添加CORS中间件支持前端跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该指定具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 启动时加载 ONNX 模型（仅在非重载模式下）
if not onnx_service.model_loaded:
    try:
        onnx_loaded = onnx_service.load_model(getattr(settings, 'ONNX_MODEL_PATH', None))
        if not onnx_loaded:
            print("警告: 未能加载ONNX模型，请检查 settings.ONNX_MODEL_PATH 是否正确")
    except Exception as e:
        print(f"加载ONNX模型时出错: {e}")

@app.get("/")
async def root():
    return {"message": "API服务运行正常", "status": "OK"}

@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    """上传并保存图片"""
    try:
        # 验证文件
        await validate_image_file(file)
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 保存原始文件
        original_filename = f"{task_id}_original{os.path.splitext(file.filename)[1]}"
        original_path = await save_upload_file(
            file, 
            "uploads/original",
            original_filename
        )
        
        return JSONResponse({
            "success": True,
            "task_id": task_id,
            "message": "图片上传成功",
            "original_url": f"/api/files/original/{original_filename}",
            "file_size": os.path.getsize(original_path),
            "saved_path": original_path
        })
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

@app.get("/api/files/{file_type}/{filename}")
async def get_file(file_type: str, filename: str):
    """获取文件"""
    if file_type not in ["original", "processed"]:
        raise HTTPException(status_code=400, detail="无效的文件类型")
    
    file_path = f"uploads/{file_type}/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(file_path)

# 同时上传两张图并进行处理
@app.post("/api/process", response_model=ProcessResponse)
async def process_images(query: UploadFile = File(...), gerber: UploadFile = File(...), model: str = "256"):
    try:
        # 校验两个文件
        await validate_image_file(query)
        await validate_image_file(gerber)

        # 读取二进制并转base64
        query_bytes = await query.read()
        gerber_bytes = await gerber.read()

        import base64
        query_b64 = base64.b64encode(query_bytes).decode("utf-8")
        gerber_b64 = base64.b64encode(gerber_bytes).decode("utf-8")

        # 调用服务进行处理
        result = await image_service.process_pcb_images(query_b64, gerber_b64, model)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

# 额外的两个单文件上传接口，分别用于上传查询图与Gerber图
@app.post("/api/upload/query")
async def upload_query_image(file: UploadFile = File(...)):
    try:
        await validate_image_file(file)
        task_id = str(uuid.uuid4())
        original_filename = f"{task_id}_query{os.path.splitext(file.filename)[1]}"
        original_path = await save_upload_file(
            file,
            "uploads/original",
            original_filename
        )
        return JSONResponse({
            "success": True,
            "task_id": task_id,
            "message": "查询图上传成功",
            "original_url": f"/api/files/original/{original_filename}",
            "file_size": os.path.getsize(original_path),
            "saved_path": original_path
        })
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

@app.post("/api/upload/gerber")
async def upload_gerber_image(file: UploadFile = File(...)):
    try:
        await validate_image_file(file)
        task_id = str(uuid.uuid4())
        original_filename = f"{task_id}_gerber{os.path.splitext(file.filename)[1]}"
        original_path = await save_upload_file(
            file,
            "uploads/original",
            original_filename
        )
        return JSONResponse({
            "success": True,
            "task_id": task_id,
            "message": "Gerber图上传成功",
            "original_url": f"/api/files/original/{original_filename}",
            "file_size": os.path.getsize(original_path),
            "saved_path": original_path
        })
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

if __name__ == "__main__":
    print(f"启动服务: http://{settings.HOST}:{settings.PORT}")
    print("按 Ctrl+C 停止服务")
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST, 
        port=settings.PORT, 
        reload=False,  # 生产环境建议关闭热重载以避免ONNX模型重复加载
        log_level="info"
    )