# evaluation/run_report_generation_test.py
import sys
from pathlib import Path

# Add the `src` directory to the Python path, to make it easier to importprojectModule
# Get the absolute path of the current script
current_script_path = Path(__file__).resolve()
# GetGetproject root directory (064_StoreTool)
project_root = current_script_path.parent.parent
# GetGet src Directory
src_path = project_root / "src"
# Add the `src` directory to `sys.path`
sys.path.insert(0, str(src_path))

from store_forecasting_tool.core import project_manager as pm
from store_forecasting_tool.analysis import prediction_engine, cost_analyzer
from store_forecasting_tool.cli import report_generator

def run_test():
    """
    A simple script, UseAtLoad Project、RunAnalysisandGenerateMarkdownReport, 
    to bypass interactive CLI input issues.
    """
    print("--- StartingAutomatedReport GenerationTest ---")

    # 1. FixedPositionandLoad Project
    project_file_path = src_path / "data" / "projects" / "MyFirstStore.json"
    if not project_file_path.exists():
        print(f"Error: Test project file notfindtoAt {project_file_path}")
        return

    print(f"Loading test project: {project_file_path.name}...")
    project = pm.load_project(project_file_path)
    if not project:
        print("Project load failed！")
        return
    print("Project loaded successfully.")

    # 2. RunAnalysis
    print("CorrectinExecuteAnalysis...")
    prediction_results = prediction_engine.predict_daily_orders(project)
    analysis_results = cost_analyzer.analyze_costs_and_profits(project, prediction_results)
    extra_analysis = cost_analyzer.perform_sensitivity_analysis(project, analysis_results)
    analysis_results.update(extra_analysis)
    print("AnalysisCompleteSuccess.")

    # 3. GenerateMarkdownReport
    print("CorrectinGenerateMarkdownReport...")
    try:
        report_path_str = report_generator.generate_md_report(project, analysis_results)
        report_path = Path(report_path_str)
        
        # 4. Verification Results
        if report_path.exists() and report_path.stat().st_size > 0:
            print(f"\n--- TestSuccess！---")
            print(f"MarkdownReportAlreadySuccessGenerateAt: {report_path.relative_to(project_root)}")
        else:
            print(f"\n--- Test Failed！---")
            print("ReportFileNotCreateorFileasEmpty.")
            
    except Exception as e:
        print(f"\n--- Test Failed！---")
        print(f"GenerateReportTimeSendNativeError: {e}")

if __name__ == "__main__":
    run_test()
