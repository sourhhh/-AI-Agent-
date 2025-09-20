#!/usr/bin/env python3
"""
手动测试脚本 - 修复版
"""

import os
import sys

sys.path.append('.')

from agents.code_fixer import CodeFixerAgent
from schemas import RepairPlan, DefectReport, Defect, FileDefects, RepairTask


def test_manual_fix():
    """手动测试代码修复"""

    # 设置API密钥（如果还没设置环境变量）
    if not os.getenv('DEEPSEEK_API_KEY'):
        api_key = input("请输入您的DeepSeek API密钥: ")
        os.environ['DEEPSEEK_API_KEY'] = api_key

    agent = CodeFixerAgent()

    # 创建测试代码
    test_code = """
def calculate_expression(expr):
    result = eval(expr)  # 不安全的使用
    return result

def process_data(data):
    return data * 2
"""

    # 创建测试文件
    test_file = "test_example.py"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_code)

    try:
        # 创建缺陷对象（不是字典！）
        defect = Defect(
            type="security",
            message="Use of insecure function 'eval'",
            line_number=3,
            severity="CRITICAL",
            tool="bandit",
            confidence=0.95
        )

        # 创建文件缺陷对象
        file_defects = FileDefects(
            file_path=test_file,
            defects=[defect]
        )

        # 创建缺陷报告对象
        defect_report = DefectReport(
            files=[file_defects],
            summary={"CRITICAL": 1, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        )

        # 创建修复任务对象
        repair_task = RepairTask(
            file_path=test_file,
            defect_index=0,
            strategy="replace_eval_with_ast_literal_eval",
            priority="CRITICAL",
            context={
                "vulnerable_function": "eval",
                "safe_replacement": "ast.literal_eval"
            }
        )

        # 创建修复计划对象
        repair_plan = RepairPlan(
            tasks=[repair_task],
            total_tasks=1
        )

        print("🔄 开始修复代码...")
        result_json = agent.fix_code(
            repair_plan.to_json(),  # 转换为JSON字符串
            defect_report.to_json()  # 转换为JSON字符串
        )

        # 解析结果
        from schemas import FixResult
        result = FixResult.from_json(result_json)

        print("✅ 修复完成！")
        print(f"策略: {result.strategy_used}")
        print(f"置信度: {result.confidence}")
        print("\n📝 修改内容:")
        for change in result.changes_made:
            print(f"  - {change}")

        print("\n📄 修复后的代码:")
        print(result.fixed_code)

    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)


if __name__ == "__main__":
    test_manual_fix()