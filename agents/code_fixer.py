import json
import logging
import re
from typing import Dict, List, Optional, Tuple

from schemas.defect_report import DefectReport, FileDefects, Defect
from schemas.fix_result import FixResult
from schemas.repair_plan import RepairTask, RepairPlan
from utils.file_utils import read_file, write_file
from utils.ai_fixer import ai_fixer  # 导入AI修复引擎
from config import Config

logger = logging.getLogger(__name__)


class CodeFixerAgent:
    def __init__(self):
        self.strategies = {
            "replace_eval_with_ast_literal_eval": self._replace_eval_strategy,
            "fix_syntax_error": self._fix_syntax_error_strategy,
            "add_null_check": self._add_null_check_strategy,
            "fix_indentation": self._fix_indentation_strategy,
            "add_type_hint": self._add_type_hint_strategy,
            "ai_automatic_fix": self._ai_automatic_fix_strategy,
        }

    def fix_code(self, repair_plan_json: str, defect_report_json: str) -> str:
        """
        根据修复计划修复代码
        """
        try:
            repair_plan = RepairPlan.from_json(repair_plan_json)
            defect_report = DefectReport.from_json(defect_report_json)

            fix_results = []
            for task in repair_plan.tasks:
                fix_result = self._execute_repair_task(task, defect_report)
                if fix_result:
                    fix_results.append(fix_result)

            if fix_results:
                return fix_results[0].to_json()
            else:
                return FixResult(
                    file_path="",
                    original_code="",
                    fixed_code="",
                    strategy_used="no_fix_applied",
                    changes_made=["无修复任务或所有修复都失败了"],
                    confidence=0.0
                ).to_json()

        except Exception as e:
            logger.error(f"修复代码时发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return FixResult(
                file_path="",
                original_code="",
                fixed_code="",
                strategy_used="error",
                changes_made=[f"修复失败: {str(e)}"],
                confidence=0.0
            ).to_json()

    def _execute_repair_task(self, task: RepairTask, defect_report: DefectReport) -> Optional[FixResult]:
        """执行单个修复任务"""
        try:
            # 找到对应的文件缺陷
            file_defects = self._find_file_defects(task.file_path, defect_report)
            if not file_defects or not file_defects.defects:
                logger.warning(f"未找到文件缺陷或缺陷列表为空: {task.file_path}")
                return None

            # 获取具体的缺陷
            if task.defect_index >= len(file_defects.defects):
                logger.warning(f"缺陷索引超出范围: {task.defect_index} (最大索引: {len(file_defects.defects) - 1})")
                return None

            defect = file_defects.defects[task.defect_index]

            # 读取原始代码
            try:
                original_code = read_file(task.file_path)
            except Exception as e:
                logger.error(f"读取文件失败: {task.file_path}, 错误: {str(e)}")
                return None

            # 添加调试信息
            print(f"🔧 执行修复任务: 文件={task.file_path}, 行号={defect.line_number}, 策略={task.strategy}")
            print(f"缺陷信息: {defect.message}")
            print(
                f"原始代码行: {original_code.splitlines()[defect.line_number - 1] if defect.line_number <= len(original_code.splitlines()) else 'N/A'}")

            strategy_func = self.strategies.get(task.strategy)
            if not strategy_func:
                logger.warning(f"未知的修复策略: {task.strategy}")
                # 尝试使用AI自动修复
                fixed_code, changes = self._ai_automatic_fix_strategy(original_code, defect, task.context)
            else:
                # 执行修复
                fixed_code, changes = strategy_func(original_code, defect, task.context)

            # 添加修复后的调试信息
            print(f"修复结果: {changes}")
            print(f"修复后代码片段:\n{fixed_code[:200]}...")

            return FixResult(
                file_path=task.file_path,
                original_code=original_code,
                fixed_code=fixed_code,
                strategy_used=task.strategy,
                changes_made=changes,
                confidence=0.9
            )

        except Exception as e:
            logger.error(f"执行修复任务时发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def _find_file_defects(self, file_path: str, defect_report: DefectReport) -> Optional[FileDefects]:
        """查找文件的缺陷信息"""
        for file_defects in defect_report.files:
            if file_defects.file_path == file_path:
                return file_defects
        return None

    def _replace_eval_strategy(self, code: str, defect: Defect, context: Dict) -> Tuple[str, List[str]]:
        """替换eval函数的策略"""
        changes = []

        # 分割代码行
        lines = code.split('\n')

        # 检查是否在指定行有eval调用
        if 0 < defect.line_number <= len(lines):
            line_index = defect.line_number - 1
            line_content = lines[line_index]

            # 检查这一行是否有eval调用
            if 'eval(' in line_content:
                # 首先确保导入了ast
                if 'import ast' not in code:
                    # 找到合适的导入位置
                    import_inserted = False
                    for i, line in enumerate(lines):
                        if line.strip().startswith('import ') or line.strip().startswith('from '):
                            # 在现有导入后添加
                            lines.insert(i + 1, 'import ast')
                            import_inserted = True
                            changes.append("添加了 import ast")
                            break
                        elif line.strip() and not line.strip().startswith('#'):
                            # 在代码开始前添加
                            lines.insert(0, 'import ast')
                            import_inserted = True
                            changes.append("添加了 import ast")
                            break

                    if not import_inserted:
                        lines.insert(0, 'import ast')
                        changes.append("添加了 import ast")

                # 替换当前行的eval调用
                fixed_line = line_content.replace('eval(', 'ast.literal_eval(')
                lines[line_index] = fixed_line
                changes.append(f"将第{defect.line_number}行的eval()替换为ast.literal_eval()")

                fixed_code = '\n'.join(lines)
                return fixed_code, changes
            else:
                changes.append(f"第{defect.line_number}行没有找到eval调用")
        else:
            changes.append(f"行号{defect.line_number}超出范围")

        return code, changes

    def _fix_syntax_error_strategy(self, code: str, defect: Defect, context: Dict) -> Tuple[str, List[str]]:
        """修复语法错误的策略"""
        changes = []
        lines = code.split('\n')
        fixed = False

        if 0 < defect.line_number <= len(lines):
            line_index = defect.line_number - 1
            problematic_line = lines[line_index]

            # 修复赋值操作符错误 (= 应该是 == 或 is)
            if '= None' in problematic_line and '==' not in problematic_line and 'if' in problematic_line:
                # 在条件语句中，= 应该是 == 或 is None
                if 'is' in problematic_line or 'is not' in problematic_line:
                    fixed_line = problematic_line.replace('= None', 'is None')
                else:
                    fixed_line = problematic_line.replace('= None', '== None')
                lines[line_index] = fixed_line
                changes.append(f"修复第{defect.line_number}行的语法错误：将=改为==")
                fixed = True

            # 修复缺少冒号
            elif re.search(r'^(?:\s*)(?:for|if|while|def|class|elif|else|try|except|finally)\b',
                           problematic_line) and not problematic_line.rstrip().endswith(':'):
                if not problematic_line.strip().endswith(':'):
                    fixed_line = problematic_line.rstrip() + ':'
                    lines[line_index] = fixed_line
                    changes.append(f"修复第{defect.line_number}行的语法错误：添加冒号")
                    fixed = True

        fixed_code = '\n'.join(lines)

        if not fixed:
            # 如果规则修复失败，尝试使用AI修复
            ai_result = ai_fixer.fix_with_ai(code, defect.message, "", "python")
            if ai_result["success"]:
                changes.append("使用AI修复语法错误")
                return ai_result["fixed_code"], changes
            changes.append("无法自动修复该语法错误")

        return fixed_code, changes

    def _add_null_check_strategy(self, code: str, defect: Defect, context: Dict) -> Tuple[str, List[str]]:
        """添加空值检查的策略"""
        changes = []
        lines = code.split('\n')

        if 0 < defect.line_number <= len(lines):
            line_index = defect.line_number - 1
            current_line = lines[line_index]

            variable_match = re.search(r'(\w+)\s*=', current_line)
            if variable_match:
                variable_name = variable_match.group(1)

                check_code = f"    if {variable_name} is None:\n        raise ValueError(\"{variable_name} cannot be None\")"
                lines.insert(line_index + 1, check_code)
                changes.append(f"在第{defect.line_number + 1}行添加了空值检查")

        fixed_code = '\n'.join(lines)
        if not changes:
            changes.append("无法添加空值检查")

        return fixed_code, changes

    def _fix_indentation_strategy(self, code: str, defect: Defect, context: Dict) -> Tuple[str, List[str]]:
        """修复缩进错误的策略"""
        # 使用AI修复缩进问题
        ai_result = ai_fixer.fix_with_ai(code, "缩进错误，请修复代码缩进", "", "python")
        if ai_result["success"]:
            return ai_result["fixed_code"], ["使用AI修复缩进错误"]
        return code, ["缩进修复失败"]

    def _add_type_hint_strategy(self, code: str, defect: Defect, context: Dict) -> Tuple[str, List[str]]:
        """添加类型提示的策略"""
        # 使用AI添加类型提示
        ai_result = ai_fixer.fix_with_ai(code, "请为代码添加适当的类型提示", "", "python")
        if ai_result["success"]:
            return ai_result["fixed_code"], ["使用AI添加类型提示"]
        return code, ["类型提示添加失败"]

    def _ai_automatic_fix_strategy(self, code: str, defect: Defect, context: Dict) -> Tuple[str, List[str]]:
        """AI自动修复策略（通用策略）"""
        if not ai_fixer.is_available():
            logger.warning("AI修复引擎不可用，无法进行自动修复")
            return code, ["AI修复引擎不可用"]

        logger.info(f"使用AI自动修复策略处理缺陷: {defect.message}")

        ai_result = ai_fixer.fix_with_ai(code, defect.message, "", "python")

        if ai_result["success"]:
            changes = [f"使用AI自动修复: {defect.message}"]
            return ai_result["fixed_code"], changes
        else:
            logger.warning(f"AI修复失败: {ai_result['error_message']}")
            return code, [f"AI修复失败: {ai_result['error_message']}"]

    def multi_round_fix(self, initial_fix_result: str, feedback: str, max_retries: int = 3) -> str:
        """
        多轮修复机制
        """
        try:
            fix_result = FixResult.from_json(initial_fix_result)

            if not ai_fixer.is_available():
                logger.warning("AI修复引擎不可用，无法进行多轮修复")
                return initial_fix_result

            # 使用AI进行多轮修复
            ai_result = ai_fixer.fix_with_ai(
                fix_result.fixed_code,
                f"之前的修复反馈: {feedback}. 请重新修复代码。",
                fix_result.original_code,
                "python"
            )

            if ai_result["success"]:
                new_result = FixResult(
                    file_path=fix_result.file_path,
                    original_code=fix_result.original_code,
                    fixed_code=ai_result["fixed_code"],
                    strategy_used=fix_result.strategy_used + "_round2",
                    changes_made=fix_result.changes_made + [f"根据反馈重新修复: {feedback}"],
                    confidence=min(fix_result.confidence + 0.1, 1.0)
                )
                return new_result.to_json()

            return initial_fix_result

        except Exception as e:
            logger.error(f"多轮修复时发生错误: {str(e)}")
            return initial_fix_result