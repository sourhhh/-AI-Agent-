# test_specific_fixes.py
import sys

sys.path.append('.')

from agents.code_fixer import CodeFixerAgent
from schemas import Defect, FileDefects, DefectReport, RepairTask, RepairPlan


def test_eval_fix():
    """专门测试eval修复"""
    print("测试eval修复...")

    agent = CodeFixerAgent()

    test_code = """
def calculate_expression(expr):
    result = eval(expr)
    return result
"""

    # 创建缺陷报告
    defect = Defect(
        type="security",
        message="Use of insecure eval",
        line_number=3,
        severity="CRITICAL",
        tool="bandit",
        confidence=0.95
    )

    file_defects = FileDefects(
        file_path="test.py",
        defects=[defect]
    )

    defect_report = DefectReport(files=[file_defects])

    # 创建修复计划
    repair_task = RepairTask(
        file_path="test.py",
        defect_index=0,
        strategy="replace_eval_with_ast_literal_eval",
        priority="CRITICAL"
    )

    repair_plan = RepairPlan(tasks=[repair_task])

    # 执行修复
    result_json = agent.fix_code(repair_plan.to_json(), defect_report.to_json())
    print("修复结果:", result_json)


if __name__ == "__main__":
    test_eval_fix()