<<<<<<< HEAD
#!/usr/bin/env python3
"""
Code Fixer Agent 主程序
"""
import json
import logging
from agents.code_fixer import CodeFixerAgent

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """主函数"""
    agent = CodeFixerAgent()

    # 示例用法
    repair_plan_json = '''
    {
        "tasks": [
            {
                "file_path": "test_file.py",
                "defect_index": 0,
                "strategy": "replace_eval_with_ast_literal_eval",
                "priority": "CRITICAL",
                "context": {
                    "vulnerable_function": "eval",
                    "safe_replacement": "ast.literal_eval"
                }
            }
        ],
        "total_tasks": 1
    }
    '''

    defect_report_json = '''
    {
        "files": [
            {
                "file_path": "test_file.py",
                "defects": [
                    {
                        "type": "security",
                        "message": "Use of insecure function 'eval'",
                        "line_number": 2,
                        "severity": "CRITICAL",
                        "tool": "bandit",
                        "confidence": 0.95
                    }
                ]
            }
        ],
        "summary": {
            "CRITICAL": 1,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0
        }
    }
    '''

    try:
        logger.info("开始修复代码...")
        result = agent.fix_code(repair_plan_json, defect_report_json)

        fix_result = json.loads(result)
        logger.info(f"修复完成！策略: {fix_result.get('strategy_used')}")
        logger.info(f"修改内容: {fix_result.get('changes_made')}")

    except Exception as e:
        logger.error(f"修复过程中发生错误: {str(e)}")


if __name__ == "__main__":
    main()
=======
from agents.project_analysis.project_analyzer import ProjectAnalyzer
from agents.defect_detection.defect_detector import DefectDetector
from agents.decision_management.decision_manager import DecisionManager

def run_system(project_path):
    # 1. 项目分析
    project_analyzer = ProjectAnalyzer()
    project_context = project_analyzer.get_project_context(project_path)

    # 2. 缺陷检测
    defect_detector = DefectDetector()
    defects = defect_detector.detect_defects(project_context)

    # 3. 决策管理与代码修复
    decision_manager = DecisionManager()
    fixed_results = decision_manager.manage_defects(defects)

    # 4. 生成最终报告
    final_report = decision_manager.generate_final_report(defects, fixed_results)
    return final_report

if __name__ == "__main__":
    sample_project_path = "examples/sample_project"
    result = run_system(sample_project_path)
    print("Final Report:", result)
>>>>>>> 3814c3f228b1518a4c31451ca7cb372f1d2e6a9e
