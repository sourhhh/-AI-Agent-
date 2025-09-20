#!/usr/bin/env python3
"""
调试脚本 - 找出具体问题位置
"""

import os
import sys
import json

sys.path.append('.')

from agents.code_fixer import CodeFixerAgent
from schemas import RepairPlan, DefectReport, Defect, FileDefects, RepairTask


def debug_fix():
    """调试修复过程"""

    print("🐛 开始调试...")

    agent = CodeFixerAgent()

    # 创建测试代码
    test_code = """
def calculate_expression(expr):
    result = eval(expr)
    return result
"""

    test_file = "debug_test.py"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_code)

    try:
        # 1. 创建缺陷对象
        defect = Defect(
            type="security",
            message="Use of insecure function 'eval'",
            line_number=3,
            severity="CRITICAL",
            tool="bandit",
            confidence=0.95
        )
        print("✅ Defect 对象创建成功")

        # 2. 创建文件缺陷对象
        file_defects = FileDefects(
            file_path=test_file,
            defects=[defect]
        )
        print("✅ FileDefects 对象创建成功")

        # 3. 创建缺陷报告对象
        defect_report = DefectReport(
            files=[file_defects],
            summary={"CRITICAL": 1}
        )
        print("✅ DefectReport 对象创建成功")

        # 4. 创建修复任务对象
        repair_task = RepairTask(
            file_path=test_file,
            defect_index=0,
            strategy="replace_eval_with_ast_literal_eval",
            priority="CRITICAL",
            context={"test": "value"}
        )
        print("✅ RepairTask 对象创建成功")

        # 5. 创建修复计划对象
        repair_plan = RepairPlan(
            tasks=[repair_task],
            total_tasks=1
        )
        print("✅ RepairPlan 对象创建成功")

        # 6. 转换为JSON
        repair_plan_json = repair_plan.to_json()
        defect_report_json = defect_report.to_json()

        print("📋 RepairPlan JSON:")
        print(repair_plan_json[:200] + "...")

        print("📋 DefectReport JSON:")
        print(defect_report_json[:200] + "...")

        # 7. 测试从JSON还原
        try:
            repair_plan_restored = RepairPlan.from_json(repair_plan_json)
            print("✅ RepairPlan 从JSON还原成功")

            defect_report_restored = DefectReport.from_json(defect_report_json)
            print("✅ DefectReport 从JSON还原成功")

            # 检查还原后的对象
            print(f"还原后 RepairTask file_path: {repair_plan_restored.tasks[0].file_path}")
            print(f"还原后 FileDefects file_path: {defect_report_restored.files[0].file_path}")

        except Exception as e:
            print(f"❌ JSON还原失败: {e}")
            import traceback
            traceback.print_exc()
            return

        # 8. 执行修复
        print("🔄 开始执行修复...")
        result_json = agent.fix_code(repair_plan_json, defect_report_json)

        print("📋 修复结果JSON:")
        print(result_json)

        from schemas import FixResult
        result = FixResult.from_json(result_json)

        print("✅ 修复完成！")
        print(f"策略: {result.strategy_used}")
        print(f"文件: {result.file_path}")

    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


if __name__ == "__main__":
    debug_fix()