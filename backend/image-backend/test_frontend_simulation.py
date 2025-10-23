#!/usr/bin/env python3
"""
模拟前端请求测试 - 验证后端接口的完整性和响应格式
"""

import requests
import json
import os
from PIL import Image
import io

def test_frontend_simulation():
    """模拟前端请求，测试完整的API响应"""
    print("🌐 模拟前端请求测试")
    print("=" * 50)
    
    # 1. 健康检查
    print("1️⃣ 测试健康检查...")
    try:
        response = requests.get('http://127.0.0.1:8000/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 健康检查通过: {data}")
        else:
            print(f"   ❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 健康检查异常: {e}")
        return False
    
    # 2. 创建测试图片
    print("\n2️⃣ 准备测试图片...")
    os.makedirs('test_images', exist_ok=True)
    
    # 创建模拟的查询图片和Gerber图片
    query_img = Image.new('RGB', (300, 200), color='red')
    gerber_img = Image.new('RGB', (300, 200), color='blue')
    
    query_img.save('test_images/sim_query.png')
    gerber_img.save('test_images/sim_gerber.png')
    print("   ✅ 测试图片创建完成")
    
    # 3. 模拟前端图片处理请求
    print("\n3️⃣ 模拟前端图片处理请求...")
    try:
        with open('test_images/sim_query.png', 'rb') as f1, open('test_images/sim_gerber.png', 'rb') as f2:
            response = requests.post(
                'http://127.0.0.1:8000/api/process',
                files={
                    'query': ('query.png', f1, 'image/png'),
                    'gerber': ('gerber.png', f2, 'image/png')
                },
                data={'model': '256'},
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ 图片处理请求成功")
            
            # 验证响应格式
            print("\n4️⃣ 验证响应格式...")
            required_fields = ['convertedGerber', 'anomalyImage', 'anomalyScore', 'defectDescription']
            missing_fields = [field for field in required_fields if field not in result]
            
            if missing_fields:
                print(f"   ❌ 缺少字段: {missing_fields}")
                return False
            else:
                print("   ✅ 响应格式完整")
            
            # 验证数据类型
            print("\n5️⃣ 验证数据类型...")
            score = result['anomalyScore']
            desc = result['defectDescription']
            converted = result['convertedGerber']
            anomaly = result['anomalyImage']
            
            checks = [
                (isinstance(score, (int, float)), f"anomalyScore 类型错误: {type(score)}"),
                (isinstance(desc, str), f"defectDescription 类型错误: {type(desc)}"),
                (isinstance(converted, str), f"convertedGerber 类型错误: {type(converted)}"),
                (isinstance(anomaly, str), f"anomalyImage 类型错误: {type(anomaly)}"),
                (0 <= score <= 1, f"anomalyScore 范围错误: {score}"),
                (len(converted) > 100, f"convertedGerber 长度异常: {len(converted)}"),
                (len(anomaly) > 100, f"anomalyImage 长度异常: {len(anomaly)}")
            ]
            
            all_passed = True
            for check, error_msg in checks:
                if not check:
                    print(f"   ❌ {error_msg}")
                    all_passed = False
            
            if all_passed:
                print("   ✅ 数据类型验证通过")
            
            # 验证图片数据
            print("\n6️⃣ 验证返回的图片数据...")
            try:
                import base64
                
                # 验证convertedGerber图片
                converted_bytes = base64.b64decode(converted)
                converted_img = Image.open(io.BytesIO(converted_bytes))
                print(f"   ✅ convertedGerber 图片有效: {converted_img.size}")
                
                # 验证anomalyImage图片
                anomaly_bytes = base64.b64decode(anomaly)
                anomaly_img = Image.open(io.BytesIO(anomaly_bytes))
                print(f"   ✅ anomalyImage 图片有效: {anomaly_img.size}")
                
            except Exception as e:
                print(f"   ❌ 图片数据验证失败: {e}")
                all_passed = False
            
            # 输出最终结果
            print("\n7️⃣ 测试结果总结...")
            print(f"   异常分数: {score:.3f}")
            print(f"   缺陷描述: {desc}")
            print(f"   判定结果: {'异常' if score > 0.35 else '正常'}")
            print(f"   转换图片: {len(converted)} 字符")
            print(f"   异常图片: {len(anomaly)} 字符")
            
            if all_passed:
                print("\n🎉 前端模拟测试通过！")
                print("✅ 后端接口完全兼容前端集成")
                return True
            else:
                print("\n⚠️ 前端模拟测试部分失败")
                return False
                
        else:
            print(f"   ❌ 图片处理失败: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   错误信息: {error_data}")
            except:
                print(f"   错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
        return False

def test_cors_headers():
    """测试CORS头信息"""
    print("\n🌐 测试CORS支持...")
    try:
        response = requests.get(
            'http://127.0.0.1:8000/',
            headers={'Origin': 'http://localhost:3000'}
        )
        
        cors_headers = [h for h in response.headers.keys() if 'access-control' in h.lower()]
        if cors_headers:
            print("   ✅ CORS头信息存在")
            for header in cors_headers:
                print(f"     {header}: {response.headers[header]}")
        else:
            print("   ⚠️  CORS头信息缺失（可能需要重启服务）")
            
    except Exception as e:
        print(f"   ❌ CORS测试失败: {e}")

def main():
    """主测试函数"""
    print("🚀 前端协作测试开始")
    print("=" * 50)
    
    # 测试前端模拟
    success = test_frontend_simulation()
    
    # 测试CORS
    test_cors_headers()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 所有测试通过！后端已准备好与前端协作")
        print("\n📋 前端集成要点:")
        print("   - API地址: http://127.0.0.1:8000")
        print("   - 主要接口: POST /api/process")
        print("   - 响应格式: JSON (包含4个字段)")
        print("   - 图片格式: Base64编码")
        print("   - 判定阈值: 0.35")
    else:
        print("❌ 测试失败，请检查后端服务状态")

if __name__ == "__main__":
    main()
