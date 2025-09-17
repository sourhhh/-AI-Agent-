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
