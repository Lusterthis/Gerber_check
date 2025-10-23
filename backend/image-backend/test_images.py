#!/usr/bin/env python3
"""
批量分析 test_images/test_images/{regular,singular} 下的图片对，
按 X.jpg 与 XG.jpg 配对调用 /api/process，输出异常分数与简要结论。
"""

import os
import requests
from typing import List, Tuple

BASE_URL = "http://127.0.0.1:8000"
ROOT_DIR = os.path.join("test_images", "test_images")
SETS = ["regular", "singular"]


def find_pairs(dir_path: str) -> List[Tuple[str, str, str]]:
    """在目录中按前缀配对 (name.jpg, nameG.jpg)。返回 (name, query_path, gerber_path)。"""
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
            pairs.append((key, os.path.join(dir_path, val["query"]), os.path.join(dir_path, val["gerber"])) )
    return pairs


def analyze_pair(query_path: str, gerber_path: str):
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
    print("开始批量分析...")
    summary = []
    for subset in SETS:
        dir_path = os.path.join(ROOT_DIR, subset)
        if not os.path.isdir(dir_path):
            print(f"跳过不存在的目录: {dir_path}")
            continue
        pairs = find_pairs(dir_path)
        if not pairs:
            print(f"目录无有效配对: {dir_path}")
            continue
        print(f"\n数据集: {subset}，配对数: {len(pairs)}")
        for name, q, g in pairs:
            try:
                resp = analyze_pair(q, g)
                if resp.status_code == 200:
                    data = resp.json()
                    score = float(data.get("anomalyScore", -1))
                    desc = data.get("defectDescription", "")
                    label = "异常" if score >= 0.5 else "正常"
                    print(f"  {name}: 分数={score:.3f}  判定={label}  描述={desc}")
                    summary.append((subset, name, score, label))
                else:
                    print(f"  {name}: 请求失败 {resp.status_code} {resp.text[:120]}")
            except Exception as e:
                print(f"  {name}: 调用异常 {e}")

    # 概要
    if summary:
        print("\n=== 汇总 ===")
        for subset, name, score, label in summary:
            print(f"[{subset}] {name}: {score:.3f} -> {label}")
    else:
        print("无结果")


if __name__ == "__main__":
    main()


