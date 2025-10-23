#!/usr/bin/env python3
"""
测试新的异常判定阈值和简化描述
"""

import requests
import json
import os
from PIL import Image

def test_new_threshold():
    """测试新的0.35阈值和简化描述"""
    print("🧪 测试新的异常判定标准...")
    print("=" * 50)
    
    # 准备测试图片
    if not os.path.exists('test_images/query.png'):
        print("创建测试图片...")
        os.makedirs('test_images', exist_ok=True)
        
        img1 = Image.new('RGB', (300, 200), color='red')
        img1.save('test_images/query.png')
        
        img2 = Image.new('RGB', (300, 200), color='blue')
        img2.save('test_images/gerber.png')
    
    try:
        # 调用API获取结果
        with open('test_images/query.png', 'rb') as f1, open('test_images/gerber.png', 'rb') as f2:
            response = requests.post(
                'http://127.0.0.1:8000/api/process',
                files={
                    'query': ('query.png', f1, 'image/png'),
                    'gerber': ('gerber.png', f2, 'image/png')
                },
                data={'model': '256'},
                proxies={"http": None, "https": None}
            )
        
        if response.status_code == 200:
            result = response.json()
            
            print("📊 新的判定标准:")
            print(f"  异常分数: {result['anomalyScore']:.6f}")
            print(f"  判定阈值: 0.35")
            print(f"  判定结果: {'异常' if result['anomalyScore'] > 0.35 else '正常'}")
            print(f"  缺陷描述: {result['defectDescription']}")
            
            # 分析新的判定逻辑
            score = result['anomalyScore']
            threshold = 0.35
            
            print(f"\n🎯 判定逻辑分析:")
            print(f"  分数: {score:.6f}")
            print(f"  阈值: {threshold}")
            print(f"  比较: {score:.6f} {'>' if score > threshold else '≤'} {threshold}")
            print(f"  结果: {'检测到缺陷' if score > threshold else '电路板正常'}")
            
            print(f"\n✅ 新标准测试完成！")
            
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def explain_new_standard():
    """解释新的判定标准"""
    print("\n📋 新的异常判定标准:")
    print("=" * 50)
    
    print("🎯 判定阈值: 0.35")
    print("  分数 ≤ 0.35 → 正常")
    print("  分数 > 0.35 → 异常")
    
    print("\n📝 描述梯度（简化）:")
    print("  正常: '电路板正常，未检测到明显缺陷'")
    print("  异常: '检测到缺陷（置信度: XX.X%）：建议检查并处理'")
    
    print("\n🔄 变更说明:")
    print("  1. 阈值从 0.3 调整为 0.35")
    print("  2. 描述从4个梯度简化为2个梯度")
    print("  3. 异常描述统一为'检测到缺陷'")
    
    print("\n📊 预期效果:")
    print("  - 减少误报（提高阈值）")
    print("  - 简化用户理解（两个梯度）")
    print("  - 统一异常处理建议")

if __name__ == "__main__":
    explain_new_standard()
    test_new_threshold()
