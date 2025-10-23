# PCB缺陷检测API接口文档

## 基础信息
- **服务地址**: `http://127.0.0.1:8000`
- **协议**: HTTP
- **数据格式**: JSON, Multipart/Form-Data
- **跨域支持**: 已配置CORS

## 接口列表

### 1. 健康检查
```
GET /
```
**响应**:
```json
{
    "message": "API服务运行正常",
    "status": "OK"
}
```

### 2. 图片处理（主要接口）
```
POST /api/process
```
**请求参数**:
- `query` (FormData): 查询图片文件
- `gerber` (FormData): Gerber图片文件
- `model` (FormData, 可选): 模型版本，默认"256"

**响应格式**:
```json
{
    "convertedGerber": "base64编码的转换后图片",
    "anomalyImage": "base64编码的异常检测图片", 
    "anomalyScore": 0.481,
    "defectDescription": "检测到缺陷（置信度: 48.1%）：建议检查并处理"
}
```

**字段说明**:
- `convertedGerber`: 转换后的Gerber图片（Base64）
- `anomalyImage`: 异常检测可视化图片（Base64）
- `anomalyScore`: 异常分数（0.0-1.0）
- `defectDescription`: 缺陷描述文本

### 3. 单文件上传
```
POST /api/upload/query    # 上传查询图片
POST /api/upload/gerber   # 上传Gerber图片
```
**请求参数**: `file` (FormData)
**响应格式**:
```json
{
    "success": true,
    "task_id": "uuid",
    "message": "上传成功",
    "original_url": "/api/files/original/filename",
    "file_size": 12345,
    "saved_path": "uploads/original/filename"
}
```

### 4. 文件访问
```
GET /api/files/{file_type}/{filename}
```
**路径参数**:
- `file_type`: "original" 或 "processed"
- `filename`: 文件名

## 判定逻辑

### 异常判定标准
- **阈值**: 0.35
- **判定规则**: 
  - 分数 ≤ 0.35 → 正常
  - 分数 > 0.35 → 异常

### 描述格式
- **正常**: "电路板正常，未检测到明显缺陷"
- **异常**: "检测到缺陷（置信度: XX.X%）：建议检查并处理"

## 前端集成示例

### JavaScript
```javascript
// 处理图片
const formData = new FormData();
formData.append('query', queryFile);
formData.append('gerber', gerberFile);

const response = await fetch('http://127.0.0.1:8000/api/process', {
    method: 'POST',
    body: formData
});

const result = await response.json();

// 显示结果
console.log('异常分数:', result.anomalyScore);
console.log('缺陷描述:', result.defectDescription);

// 显示图片
const img = document.createElement('img');
img.src = `data:image/png;base64,${result.convertedGerber}`;
```

### React示例
```jsx
const handleUpload = async (queryFile, gerberFile) => {
    const formData = new FormData();
    formData.append('query', queryFile);
    formData.append('gerber', gerberFile);
    
    const response = await fetch('http://127.0.0.1:8000/api/process', {
        method: 'POST',
        body: formData
    });
    
    const result = await response.json();
    setResult(result);
};
```

## 错误处理

### 常见错误码
- `400`: 请求参数错误
- `404`: 文件不存在
- `422`: 请求格式错误
- `500`: 服务器内部错误

### 错误响应
```json
{
    "detail": "错误描述"
}
```

## 技术规格

### 文件限制
- **支持格式**: JPG, PNG, BMP, WEBP
- **文件大小**: 最大10MB
- **处理时间**: 通常2-5秒

### 性能指标
- **模型大小**: 115MB
- **输入尺寸**: 256×256×3
- **输出图片**: Base64编码
- **并发支持**: 多用户同时使用
