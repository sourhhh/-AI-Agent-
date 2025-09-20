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