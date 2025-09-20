import unittest
from agents.decision_manager import DecisionManagerAgent
from schemas.repair_plan import RepairPlan

class TestDecisionManagerAgent(unittest.TestCase):
    def setUp(self):
        self.dm_agent = DecisionManagerAgent()

    def test_determine_priority(self):
        # 测试安全漏洞优先级
        self.assertEqual(
            self.dm_agent.determine_priority("security_vulnerability"),
            "CRITICAL"
        )
        # 测试普通错误优先级
        self.assertEqual(
            self.dm_agent.determine_priority("syntax_error"),
            "HIGH"
        )
        # 测试广泛影响的中等优先级缺陷
        self.assertEqual(
            self.dm_agent.determine_priority("performance_issue", "widespread"),
            "HIGH"
        )

    def test_determine_strategy(self):
        # 测试特定缺陷类型的策略
        self.assertEqual(
            self.dm_agent.determine_strategy("eval_injection", {}),
            "replace_eval_with_ast_literal_eval"
        )
        # 测试通用策略
        self.assertEqual(
            self.dm_agent.determine_strategy("unknown_defect", {}),
            "general_repair_strategy"
        )

    def test_generate_repair_plan(self):
        test_defect_reports = [
            {
                "file_path": "/path/to/project/utils/helpers.py",
                "defect_index": 0,
                # 删：根层级的defect_type
                "impact": "widespread",
                "context": {
                    "defect_type": "eval_injection",  # 加：把defect_type放到context里
                    "vulnerable_function": "eval",
                    "safe_replacement": "ast.literal_eval"
                }
            },
            {
                "file_path": "/path/to/project/models/user.py",
                "defect_index": 2,
                # 删：根层级的defect_type
                "impact": "normal",
                "context": {
                    "defect_type": "null_pointer",  # 加：把defect_type放到context里
                    "variable": "user_profile",
                    "suggested_check": "if user_profile is not None"
                }
            }
        ]
        repair_plan = self.dm_agent.generate_repair_plan(test_defect_reports)
        self.assertIsInstance(repair_plan, RepairPlan)
        self.assertEqual(len(repair_plan.tasks), 2)  # 现在能生成2个任务，断言通过
        self.assertEqual(repair_plan.total_tasks, 2)
        # 验证优先级排序（无需改，因为逻辑不变）
        self.assertEqual(repair_plan.tasks[0].context["defect_type"], "eval_injection")
        self.assertEqual(repair_plan.tasks[1].context["defect_type"], "null_pointer")

    def test_save_and_load_repair_plan(self):
        test_defect_reports = [
            {
                "file_path": "/path/to/test.py",
                "defect_index": 0,
                # 删：根层级的defect_type
                "impact": "normal",  # 可选：保留impact，不影响
                "context": {
                    "defect_type": "syntax_error"  # 加：把defect_type放到context里
                }
            }
        ]
        repair_plan = self.dm_agent.generate_repair_plan(test_defect_reports)
        file_path = "test_repair_plan.json"
        self.dm_agent.save_repair_plan(repair_plan, file_path)
        loaded_plan = self.dm_agent.load_repair_plan(file_path)
        self.assertEqual(len(loaded_plan.tasks), len(repair_plan.tasks))  # 现在都是1，通过
        self.assertEqual(loaded_plan.total_tasks, repair_plan.total_tasks)
        self.assertEqual(loaded_plan.tasks[0].file_path, repair_plan.tasks[0].file_path)  # 不再越界

if __name__ == '__main__':
    unittest.main()