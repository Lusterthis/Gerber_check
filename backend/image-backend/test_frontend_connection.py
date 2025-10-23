#!/usr/bin/env python3
"""
测试前端与后端的连接
"""

import requests
import json
import time

def test_backend_health():
    """测试后端健康状态"""
    print("🏥 测试后端健康状态...")
    try:
        response = requests.get('http://127.0.0.1:8000/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 后端健康: {data}")
            return True
        else:
            print(f"❌ 后端不健康: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到后端: {e}")
        return False

def test_cors_headers():
    """测试CORS头信息"""
    print("\n🌐 测试CORS支持...")
    try:
        # 发送OPTIONS预检请求
        response = requests.options(
            'http://127.0.0.1:8000/api/process',
            headers={
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            },
            timeout=5
        )
        
        print(f"OPTIONS请求状态码: {response.status_code}")
        print(f"CORS头信息:")
        for header, value in response.headers.items():
            if 'access-control' in header.lower():
                print(f"  {header}: {value}")
        
        if 'Access-Control-Allow-Origin' in response.headers:
            print("✅ CORS配置正确")
            return True
        else:
            print("❌ 缺少CORS头信息")
            return False
            
    except Exception as e:
        print(f"❌ CORS测试失败: {e}")
        return False

def test_api_endpoints():
    """测试API端点可用性"""
    print("\n🔗 测试API端点...")
    
    endpoints = [
        ('GET', '/', '健康检查'),
        ('POST', '/api/upload/query', '查询图片上传'),
        ('POST', '/api/upload/gerber', 'Gerber图片上传'),
        ('POST', '/api/process', '图片处理'),
    ]
    
    results = {}
    
    for method, endpoint, description in endpoints:
        try:
            url = f'http://127.0.0.1:8000{endpoint}'
            
            if method == 'GET':
                response = requests.get(url, timeout=5)
            else:
                # 对于POST请求，发送一个简单的测试
                response = requests.post(url, timeout=5)
            
            status = "✅" if response.status_code in [200, 405, 422] else "❌"
            print(f"  {status} {method} {endpoint} - {description} ({response.status_code})")
            results[endpoint] = response.status_code
            
        except Exception as e:
            print(f"  ❌ {method} {endpoint} - {description} (错误: {e})")
            results[endpoint] = f"错误: {e}"
    
    return results

def test_frontend_simulation():
    """模拟前端请求"""
    print("\n🎭 模拟前端请求...")
    
    try:
        # 创建测试图片数据
        from PIL import Image
        import io
        import base64
        
        # 创建测试图片
        test_img = Image.new('RGB', (100, 100), color='red')
        img_buffer = io.BytesIO()
        test_img.save(img_buffer, format='PNG')
        img_data = img_buffer.getvalue()
        
        # 模拟前端上传请求
        files = {
            'query': ('test_query.png', img_data, 'image/png'),
            'gerber': ('test_gerber.png', img_data, 'image/png')
        }
        
        response = requests.post(
            'http://127.0.0.1:8000/api/process',
            files=files,
            data={'model': '256'},
            timeout=30  # 处理可能需要更长时间
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 前端模拟请求成功!")
            print(f"   异常分数: {result.get('anomalyScore', 'N/A')}")
            print(f"   缺陷描述: {result.get('defectDescription', 'N/A')}")
            print(f"   返回图片数量: {len([k for k in result.keys() if 'Image' in k or 'Gerber' in k])}")
            return True
        else:
            print(f"❌ 前端模拟请求失败: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   错误信息: {error_data}")
            except:
                print(f"   错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 前端模拟请求异常: {e}")
        return False

def generate_frontend_test_code():
    """生成前端测试代码"""
    print("\n📝 生成前端测试代码...")
    
    frontend_code = '''
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
'''
    
    with open('frontend_test.js', 'w', encoding='utf-8') as f:
        f.write(frontend_code)
    
    print("✅ 前端测试代码已生成: frontend_test.js")
    print("   可以在浏览器控制台中运行此代码进行测试")

def main():
    """主测试函数"""
    print("🚀 开始测试前端与后端连接...")
    print("=" * 50)
    
    # 1. 测试后端健康状态
    health_ok = test_backend_health()
    if not health_ok:
        print("\n❌ 后端服务不可用，请先启动后端服务")
        return
    
    # 2. 测试CORS支持
    cors_ok = test_cors_headers()
    
    # 3. 测试API端点
    api_results = test_api_endpoints()
    
    # 4. 模拟前端请求
    frontend_ok = test_frontend_simulation()
    
    # 5. 生成前端测试代码
    generate_frontend_test_code()
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print(f"  后端健康: {'✅' if health_ok else '❌'}")
    print(f"  CORS支持: {'✅' if cors_ok else '❌'}")
    print(f"  前端模拟: {'✅' if frontend_ok else '❌'}")
    
    if health_ok and cors_ok and frontend_ok:
        print("\n🎉 所有测试通过！前端可以正常连接后端")
        print("💡 建议:")
        print("   1. 将 frontend_test.js 复制到前端项目中")
        print("   2. 在浏览器控制台中运行测试代码")
        print("   3. 检查网络请求是否正常")
    else:
        print("\n⚠️  部分测试失败，请检查配置")

if __name__ == "__main__":
    main()
