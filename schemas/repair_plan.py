from typing import List, Dict, Literal
from dataclasses import dataclass, field, asdict
import json


@dataclass
class RepairTask:
    file_path: str
    defect_index: int
    strategy: str
    priority: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    context: Dict = field(default_factory=dict)


@dataclass
class RepairPlan:
    tasks: List[RepairTask] = field(default_factory=list)
    total_tasks: int = 0

    def to_json(self) -> str:
        # 保存时：将 RepariTask 对象转成字典（原逻辑不变）
        return json.dumps(asdict(self), indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> 'RepairPlan':
        data = json.loads(json_str)
        # 关键修复：将 tasks 中的每个字典转成 RepairTask 对象
        repair_tasks = []
        for task_dict in data.get("tasks", []):  # 遍历 JSON 中的 tasks 字典列表
            # 用字典构造 RepairTask 对象（字段一一对应）
            task = RepairTask(
                file_path=task_dict["file_path"],
                defect_index=task_dict["defect_index"],
                strategy=task_dict["strategy"],
                priority=task_dict["priority"],
                context=task_dict.get("context", {})
            )
            repair_tasks.append(task)
        # 用转换后的 RepairTask 列表构造 RepairPlan
        return cls(
            tasks=repair_tasks,
            total_tasks=len(repair_tasks)  # 总任务数同步更新
        )