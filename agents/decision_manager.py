import json
import logging
from dataclasses import asdict
from typing import List, Dict, Literal, Optional
# 仅保留你现有项目中存在的导入（无defect_report相关）
from schemas.repair_plan import RepairPlan, RepairTask

# 配置日志（保留原逻辑，无修改）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("decision_manager.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DecisionManagerAgent")


class DecisionManagerAgent:
    """
    决策管理器Agent：基于现有缺陷报告制定修复计划（删除defect_type依赖）

    核心功能：
    1. 分析缺陷报告，确定每个缺陷的优先级
    2. 为每个缺陷制定合适的修复策略
    3. 生成结构化的修复计划(RepairPlan)
    4. 支持修复计划的序列化和反序列化
    """

    def __init__(self):
        """初始化决策管理器，保留原优先级/策略映射（适配context传递的缺陷信息）"""
        logger.info("初始化DecisionManagerAgent...")

        # 缺陷类型到优先级的映射规则（保留原键，后续从context提取对应信息）
        self.defect_priority_rules = {
            "security_vulnerability": "CRITICAL",
            "injection_vulnerability": "CRITICAL",
            "authentication_issue": "CRITICAL",
            "syntax_error": "HIGH",
            "runtime_error": "HIGH",
            "logic_error": "HIGH",
            "performance_issue": "MEDIUM",
            "memory_leak": "MEDIUM",
            "code_smell": "MEDIUM",
            "duplicate_code": "LOW",
            "naming_issue": "LOW",
            "comment_issue": "LOW"
        }

        # 缺陷类型到修复策略的映射（保留原键，后续从context提取对应信息）
        self.defect_strategy_mapping = {
            "eval_injection": "replace_eval_with_ast_literal_eval",
            "null_pointer": "add_null_check",
            "division_by_zero": "add_divisor_check",
            "syntax_error": "fix_syntax_issue",
            "unauthorized_access": "implement_proper_auth_check",
            "hardcoded_credentials": "move_credentials_to_env",
            "duplicate_code": "extract_common_function",
            "unoptimized_loop": "optimize_loop_structure",
            "missing_error_handling": "add_exception_handling"
        }

        logger.info("DecisionManagerAgent初始化完成")

    def determine_priority(self, defect_info: str, impact: str = "normal") -> Literal[
        "CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        """
        确定缺陷的优先级（修改：参数从defect_type改为defect_info，适配context传递）

        Args:
            defect_info: 从context提取的缺陷类型信息
            impact: 缺陷影响范围，可选值: "normal", "widespread", "critical_system"

        Returns:
            优先级级别: CRITICAL, HIGH, MEDIUM, 或 LOW
        """
        logger.debug(f"为缺陷信息 '{defect_info}' 确定优先级，影响范围: {impact}")

        # 从规则中获取基础优先级（逻辑不变，参数名适配）
        base_priority = self.defect_priority_rules.get(defect_info, "MEDIUM")

        # 根据影响范围调整优先级（保留原逻辑）
        if impact == "widespread" and base_priority != "CRITICAL":
            priority_map = {
                "HIGH": "CRITICAL",
                "MEDIUM": "HIGH",
                "LOW": "MEDIUM"
            }
            adjusted_priority = priority_map.get(base_priority, base_priority)
            logger.debug(f"根据广泛影响调整优先级: {base_priority} -> {adjusted_priority}")
            return adjusted_priority

        logger.debug(f"确定优先级: {base_priority}")
        return base_priority

    def determine_strategy(self, defect_info: str, context: Dict) -> str:
        """
        确定修复策略（修改：参数从defect_type改为defect_info，适配context传递）

        Args:
            defect_info: 从context提取的缺陷类型信息
            context: 缺陷相关上下文信息

        Returns:
            修复策略标识符
        """
        logger.debug(f"为缺陷信息 '{defect_info}' 确定修复策略")

        # 尝试从映射中获取策略（逻辑不变，参数名适配）
        strategy = self.defect_strategy_mapping.get(defect_info)

        # 如果没有找到特定策略，使用通用策略（保留原逻辑）
        if not strategy:
            logger.warning(f"未找到缺陷信息 '{defect_info}' 的特定修复策略，使用通用策略")
            if "security" in defect_info:
                strategy = "apply_security_best_practices"
            elif "error" in defect_info or "issue" in defect_info:
                strategy = "fix_general_issue"
            else:
                strategy = "general_repair_strategy"

        logger.debug(f"确定修复策略: {strategy}")
        return strategy

    def generate_repair_plan(self, defect_reports: List[Dict]) -> RepairPlan:
        """
        根据缺陷报告生成修复计划（核心修改：删除defect_type提取，从context取缺陷信息）

        Args:
            defect_reports: 缺陷报告列表（你现有defect_detector_output.json的格式）

        Returns:
            生成的修复计划对象
        """
        logger.info(f"开始生成修复计划，共收到 {len(defect_reports)} 个缺陷报告")

        repair_tasks = []

        for idx, defect_report in enumerate(defect_reports):
            try:
                # 提取缺陷报告中的关键信息（删除defect_type提取，从context取缺陷信息）
                file_path = defect_report.get("file_path")
                defect_index = defect_report.get("defect_index", idx)
                impact = defect_report.get("impact", "normal")
                context = defect_report.get("context", {})

                # 从context中提取原缺陷类型信息（替代直接提取defect_type）
                defect_info = context.get("defect_type")  # 适配你现有JSON中context的结构
                if not all([file_path, defect_info]):  # 校验改为file_path和defect_info
                    logger.error(f"缺陷报告不完整（缺少文件路径或context中的缺陷信息），跳过处理: {defect_report}")
                    continue

                # 确定优先级和修复策略（参数改为defect_info）
                priority = self.determine_priority(defect_info, impact)
                strategy = self.determine_strategy(defect_info, context)

                # 创建修复任务（无defect_type字段，仅保留协议5个字段）
                task = RepairTask(
                    file_path=file_path,
                    defect_index=defect_index,
                    strategy=strategy,
                    priority=priority,
                    context=context  # 缺陷类型信息已在context中，无需额外传递
                )

                repair_tasks.append(task)
                logger.debug(f"创建修复任务: {file_path} 中的缺陷 #{defect_index}, 优先级: {priority}")

            except Exception as e:
                logger.error(f"处理缺陷报告时出错: {str(e)}", exc_info=True)
                continue

        # 按优先级排序任务（保留原逻辑）
        priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        repair_tasks.sort(key=lambda x: priority_order[x.priority])

        # 创建并返回修复计划（保留原逻辑）
        repair_plan = RepairPlan(
            tasks=repair_tasks,
            total_tasks=len(repair_tasks)
        )

        logger.info(f"修复计划生成完成，共包含 {repair_plan.total_tasks} 个任务")
        return repair_plan

    def save_repair_plan(self, repair_plan: RepairPlan, file_path: str) -> None:
        """保留原逻辑，无修改"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(repair_plan.to_json())
            logger.info(f"修复计划已保存至: {file_path}")
        except Exception as e:
            logger.error(f"保存修复计划失败: {str(e)}", exc_info=True)
            raise

    def load_repair_plan(self, file_path: str) -> RepairPlan:
        """保留原逻辑，无修改"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_str = f.read()
            repair_plan = RepairPlan.from_json(json_str)
            logger.info(f"从 {file_path} 加载修复计划，包含 {repair_plan.total_tasks} 个任务")
            return repair_plan
        except Exception as e:
            logger.error(f"加载修复计划失败: {str(e)}", exc_info=True)
            raise