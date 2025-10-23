
// 前端连接测试代码
const API_BASE_URL = 'http://127.0.0.1:8000';

// 1. 健康检查
async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/`);
        const data = await response.json();
        console.log('后端健康状态:', data);
        return response.ok;
    } catch (error) {
        console.error('后端连接失败:', error);
        return false;
    }
}

// 2. 上传并处理图片
async function processImages(queryFile, gerberFile) {
    try {
        const formData = new FormData();
        formData.append('query', queryFile);
        formData.append('gerber', gerberFile);
        formData.append('model', '256');
        
        const response = await fetch(`${API_BASE_URL}/api/process`, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('处理结果:', result);
            
            // 显示返回的图片
            if (result.convertedGerber) {
                const convertedImg = document.createElement('img');
                convertedImg.src = `data:image/png;base64,${result.convertedGerber}`;
                document.body.appendChild(convertedImg);
            }
            
            if (result.anomalyImage) {
                const anomalyImg = document.createElement('img');
                anomalyImg.src = `data:image/png;base64,${result.anomalyImage}`;
                document.body.appendChild(anomalyImg);
            }
            
            return result;
        } else {
            console.error('处理失败:', response.status, await response.text());
            return null;
        }
    } catch (error) {
        console.error('请求异常:', error);
        return null;
    }
}

// 3. 使用示例
async function testConnection() {
    console.log('开始测试后端连接...');
    
    // 检查健康状态
    const isHealthy = await checkBackendHealth();
    if (!isHealthy) {
        console.error('后端服务不可用');
        return;
    }
    
    console.log('后端服务正常，可以进行图片处理');
}

// 调用测试
testConnection();
