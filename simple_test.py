#!/usr/bin/env python3
"""
最简单的测试脚本
"""

import os
import sys

sys.path.append('.')

# 最简单的测试 - 直接测试对象创建
from schemas import RepairTask, RepairPlan, Defect, FileDefects, DefectReport


def test_basic_objects():
    """测试基本对象创建"""
    print("🧪 测试基本对象创建...")

    # 1. 测试RepairTask
    task = RepairTask(
        file_path="test.py",
        defect_index=0,
        strategy="test_strategy",
        priority="CRITICAL",
        context={}
    )
    print("✅ RepairTask 创建成功")

    # 2. 测试RepairPlan
    plan = RepairPlan(tasks=[task], total_tasks=1)
    print("✅ RepairPlan 创建成功")

    # 3. 测试JSON序列化
    plan_json = plan.to_json()
    print("✅ JSON序列化成功")

    # 4. 测试JSON反序列化
    plan_restored = RepairPlan.from_json(plan_json)
    print("✅ JSON反序列化成功")

    # 5. 检查反序列化结果
    print(f"反序列化 file_path: {plan_restored.tasks[0].file_path}")
    print(f"反序列化 strategy: {plan_restored.tasks[0].strategy}")

    print("🎉 所有基本测试通过！")


if __name__ == "__main__":
    test_basic_objects()