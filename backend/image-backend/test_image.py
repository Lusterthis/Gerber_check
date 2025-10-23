#!/usr/bin/env python3
"""
测试新的异常判定标准（0.35阈值，两个梯度）
测试 test_images/test_images/ 下的正常和异常图片各5张
"""

import requests
import json
import os
from typing import List, Tuple

BASE_URL = "http://127.0.0.1:8000"
ROOT_DIR = os.path.join("test_images", "test_images")
SETS = ["regular", "singular"]  # regular=正常, singular=异常
THRESHOLD = 0.35

def find_pairs(dir_path: str) -> List[Tuple[str, str, str]]:
    """在目录中按前缀配对 (name.jpg, nameG.jpg)。返回 (name, query_path, gerber_path)。"""
    if not os.path.exists(dir_path):
        return []
    
    files = [f for f in os.listdir(dir_path) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    names = {}
    for f in files:
        lower = f.lower()
        if lower.endswith("g.jpg") or lower.endswith("g.jpeg") or lower.endswith("g.png"):
            key = lower[:-5] if lower.endswith("g.jpg") else (lower[:-6] if lower.endswith("g.jpeg") else lower[:-5])
            names.setdefault(key, {})["gerber"] = f
        else:
            key = os.path.splitext(lower)[0]
            names.setdefault(key, {})["query"] = f

    pairs: List[Tuple[str, str, str]] = []
    for key, val in names.items():
        if "query" in val and "gerber" in val:
            pairs.append((key, os.path.join(dir_path, val["query"]), os.path.join(dir_path, val["gerber"])))
    return pairs

def analyze_pair(query_path: str, gerber_path: str):
    """分析一对图片"""
    with open(query_path, "rb") as f1, open(gerber_path, "rb") as f2:
        resp = requests.post(
            f"{BASE_URL}/api/process",
            files={
                "query": (os.path.basename(query_path), f1, "image/jpeg"),
                "gerber": (os.path.basename(gerber_path), f2, "image/jpeg"),
            },
            data={"model": "256"},
            proxies={"http": None, "https": None},
            timeout=60,
        )
    return resp

def main():
    """主测试函数"""
    print("🧪 测试新的异常判定标准（0.35阈值，两个梯度）")
    print("=" * 60)
    print(f"判定阈值: {THRESHOLD}")
    print(f"描述梯度: 正常 / 异常")
    print("=" * 60)
    
    all_results = []
    
    for subset in SETS:
        dir_path = os.path.join(ROOT_DIR, subset)
        if not os.path.isdir(dir_path):
            print(f"❌ 跳过不存在的目录: {dir_path}")
            continue
            
        pairs = find_pairs(dir_path)
        if not pairs:
            print(f"❌ 目录无有效配对: {dir_path}")
            continue
            
        print(f"\n📁 数据集: {subset} ({'正常' if subset == 'regular' else '异常'})")
        print(f"   配对数: {len(pairs)}")
        print("-" * 40)
        
        subset_results = []
        
        for name, q, g in pairs:
            try:
                resp = analyze_pair(q, g)
                if resp.status_code == 200:
                    data = resp.json()
                    score = float(data.get("anomalyScore", -1))
                    desc = data.get("defectDescription", "")
                    
                    # 新的判定逻辑
                    is_defect = score > THRESHOLD
                    expected = "异常" if subset == "singular" else "正常"
                    actual = "异常" if is_defect else "正常"
                    correct = (expected == actual)
                    
                    status = "✅" if correct else "❌"
                    
                    print(f"  {status} {name}:")
                    print(f"    分数: {score:.3f}")
                    print(f"    判定: {actual} (阈值: {THRESHOLD})")
                    print(f"    期望: {expected}")
                    print(f"    描述: {desc}")
                    print(f"    正确: {'是' if correct else '否'}")
                    
                    subset_results.append({
                        'name': name,
                        'score': score,
                        'actual': actual,
                        'expected': expected,
                        'correct': correct,
                        'description': desc
                    })
                    
                else:
                    print(f"  ❌ {name}: 请求失败 {resp.status_code}")
                    print(f"     错误: {resp.text[:100]}")
                    
            except Exception as e:
                print(f"  ❌ {name}: 调用异常 {e}")
        
        all_results.extend(subset_results)
        print(f"\n📊 {subset} 结果统计:")
        correct_count = sum(1 for r in subset_results if r['correct'])
        total_count = len(subset_results)
        accuracy = (correct_count / total_count * 100) if total_count > 0 else 0
        print(f"   正确: {correct_count}/{total_count} ({accuracy:.1f}%)")
    
    # 总体统计
    print("\n" + "=" * 60)
    print("📊 总体测试结果")
    print("=" * 60)
    
    if all_results:
        total_correct = sum(1 for r in all_results if r['correct'])
        total_count = len(all_results)
        overall_accuracy = (total_correct / total_count * 100) if total_count > 0 else 0
        
        print(f"总测试数: {total_count}")
        print(f"正确数: {total_correct}")
        print(f"准确率: {overall_accuracy:.1f}%")
        
        # 按数据集统计
        regular_results = [r for r in all_results if r['name'] in ['1233', '1267', '1301', '1317', '1436']]
        singular_results = [r for r in all_results if r['name'] in ['23', '43', '5', '56', '94']]
        
        if regular_results:
            regular_correct = sum(1 for r in regular_results if r['correct'])
            regular_accuracy = (regular_correct / len(regular_results) * 100)
            print(f"\n正常样本准确率: {regular_correct}/{len(regular_results)} ({regular_accuracy:.1f}%)")
        
        if singular_results:
            singular_correct = sum(1 for r in singular_results if r['correct'])
            singular_accuracy = (singular_correct / len(singular_results) * 100)
            print(f"异常样本准确率: {singular_correct}/{len(singular_results)} ({singular_accuracy:.1f}%)")
        
        # 分数分布
        print(f"\n📈 分数分布:")
        normal_scores = [r['score'] for r in all_results if r['expected'] == '正常']
        defect_scores = [r['score'] for r in all_results if r['expected'] == '异常']
        
        if normal_scores:
            print(f"  正常样本分数: {min(normal_scores):.3f} - {max(normal_scores):.3f} (平均: {sum(normal_scores)/len(normal_scores):.3f})")
        if defect_scores:
            print(f"  异常样本分数: {min(defect_scores):.3f} - {max(defect_scores):.3f} (平均: {sum(defect_scores)/len(defect_scores):.3f})")
        
        # 阈值效果分析
        print(f"\n🎯 阈值效果分析:")
        print(f"  阈值: {THRESHOLD}")
        false_positive = sum(1 for r in all_results if r['expected'] == '正常' and r['actual'] == '异常')
        false_negative = sum(1 for r in all_results if r['expected'] == '异常' and r['actual'] == '正常')
        print(f"  误报数 (正常→异常): {false_positive}")
        print(f"  漏报数 (异常→正常): {false_negative}")
        
        if overall_accuracy >= 80:
            print(f"\n🎉 测试通过！准确率: {overall_accuracy:.1f}%")
        else:
            print(f"\n⚠️  测试未通过，准确率: {overall_accuracy:.1f}%")
            print("建议检查阈值设置或模型性能")
            
    else:
        print("❌ 无测试结果")

if __name__ == "__main__":
    main()
