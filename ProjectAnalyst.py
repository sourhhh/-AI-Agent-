import os
import json
from pathlib import Path

class ProjectAnalyst:
    def __init__(self, project_path: str):
        # 初始化项目路径
        self.project_path = Path(project_path)

    def analyze(self):
        # 存放项目结构的字典
        project_structure = {
            "requirements": [],  # requirements.txt 中的依赖
            "python_files": [],  # 所有 .py 文件
            "test_files": []     # 所有 test_*.py 文件
        }
        test_directory = None  # 用于记录测试目录

        # 读取 requirements.txt
        req_file = self.project_path / "requirements.txt"
        if req_file.exists():
            with open(req_file, "r", encoding="utf-8") as f:
                project_structure["requirements"] = [
                    line.strip() for line in f if line.strip()
                ]

        # 遍历项目目录，查找 Python 文件
        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = str(Path(root) / file)
                    project_structure["python_files"].append(file_path)

                    # 检测 test_*.py 文件
                    if file.startswith("test_"):
                        project_structure["test_files"].append(file_path)

                        # 记录测试目录（只记录第一个找到的）
                        if test_directory is None:
                            test_directory = str(Path(root))

        # 返回分析结果
        return {
            "project_structure": project_structure,
            "test_directory": test_directory
        }


# 示例运行
if __name__ == "__main__":
    # 假设要分析 sample_project 目录
    project_path = "sample_project"
    analyst = ProjectAnalyst(project_path)
    result = analyst.analyze()

    # 美化打印输出 JSON，支持中文
    print(json.dumps(result, indent=2, ensure_ascii=False))
