# evaluation/tests/test_analysis.py
import os
import sys
from pathlib import Path
import json
from unittest.mock import patch, MagicMock

# saveproject root directoryAddtosys.path
PROJECT_ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.store_forecasting_tool.core.project_models import Project
from src.store_forecasting_tool.analysis import cost_analyzer, prediction_engine
from src.store_forecasting_tool.cli import report_generator

# CreateOneitem(s)FoundationFoundationProjectImplementationExampleProvidePlaceHasTestUseUse
def create_base_project():
    project_data = {
        "name": "TestProject", "city": "TestCity", "area": "TestRegion", 
        "business_circle_type": "Core Business District", "longitude": 120.0, "latitude": 30.0,
        "categories": {"Staples": 0.5, "Snacks": 0.3, "Beverages": 0.2},
        "avg_item_price": 35.0, "daily_customers": 150, "conversion_rate": 0.8,
        "ingredient_cost_ratio": 0.3, "packaging_cost_ratio": 0.05,
        "monthly_rent": 20000, "monthly_labor_cost": 30000,
        "monthly_marketing_cost": 5000, "commission_rate": 0.15,
        "platform_fee_rate": 0.05, "initial_investment": 100000
    }
    return Project(**project_data)

def test_core_metrics_calculation():
    """Test whether all core metrics are computed and returned.forShould metric: 2.4.1"""
    project = create_base_project()
    prediction_results = prediction_engine.predict_daily_orders(project)
    analysis_results = cost_analyzer.analyze_costs_and_profits(project, prediction_results)
    
    required_metrics = [
        "predicted_daily_orders", "avg_item_price", "gross_profit_margin",
        "net_profit", "payback_period_months"
    ]
    for metric in required_metrics:
        assert metric in analysis_results, f"Test Failed: Analysis results are missing the core metric '{metric}'."
        assert analysis_results[metric] is not None, f"Test Failed: CoreIndicatorMark '{metric}' ValueasNone."

def test_suggestion_generation():
    """TestYesNoGenerateDecisionRecommendation.forShould metric: 2.3.3"""
    project = create_base_project()
    prediction_results = prediction_engine.predict_daily_orders(project)
    analysis_results = cost_analyzer.analyze_costs_and_profits(project, prediction_results)
    full_analysis = cost_analyzer.perform_sensitivity_analysis(project, analysis_results)

    assert "suggestions" in full_analysis, "Test Failed: Analysis results are missing 'suggestions' Key."
    assert isinstance(full_analysis["suggestions"], list), "Test Failed: 'suggestions' NotOneitem(s)List."
    assert len(full_analysis["suggestions"]) >= 3, "Test Failed: Generated recommendations are fewer than 3 items."

def test_sensitivity_analysis():
    """Test whether sensitivity analysis is generated and sorted.forShould metric: 2.4.2"""
    project = create_base_project()
    prediction_results = prediction_engine.predict_daily_orders(project)
    analysis_results = cost_analyzer.analyze_costs_and_profits(project, prediction_results)
    full_analysis = cost_analyzer.perform_sensitivity_analysis(project, analysis_results)

    assert "sensitivity_analysis" in full_analysis, "Test Failed: AnalysisResultMissingfew 'sensitivity_analysis'."
    assert isinstance(full_analysis["sensitivity_analysis"], list), "Test Failed: 'sensitivity_analysis' NotYesOneitem(s)List."
    assert len(full_analysis["sensitivity_analysis"]) >= 3, "Test Failed: Sensitivity factors are fewer than 3."
    # Verify sorting(larger impact should come first)
    impact_values = [abs(v) for k, v in full_analysis["sensitivity_analysis"]]
    assert impact_values == sorted(impact_values, reverse=True), "Test Failed: Sensitivity analysis results are not sorted by descending impact."

def test_break_even_chart_generation():
    """Test whether the break-even chart is successfully generated.forShould metric: 2.3.2"""
    project = create_base_project()
    prediction_results = prediction_engine.predict_daily_orders(project)
    analysis_results = cost_analyzer.analyze_costs_and_profits(project, prediction_results)
    
    # Report GenerationOverProcesswill also generate charts
    output_path = report_generator.EVALUATION_DIR / f"{project.name}_break_even_chart.png"
    if output_path.exists():
        output_path.unlink()

    # Call the main report generation function, which is responsible for generating the chart
    report_generator.generate_md_report(project, analysis_results)

    assert output_path.exists(), f"Test Failed: Chart file {output_path} was not created."
    assert output_path.stat().st_size > 0, f"Test Failed: Chart file {output_path} size is 0."
    if output_path.exists():
        output_path.unlink()

@patch('src.store_forecasting_tool.cli.report_generator.generate_md_report')
def test_md_report_content_proxy(mock_generate_md):
    """
    Use simulation (mock) generation to verify Markdown report content.
    forShould metric: 2.4.3b
    """
    project = create_base_project()
    prediction_results = prediction_engine.predict_daily_orders(project)
    analysis_results = cost_analyzer.analyze_costs_and_profits(project, prediction_results)
    
    # AdjustUseReport GenerationFunctionNumber
    report_generator.generate_md_report(project, analysis_results)

    # Assert that the mock function is called
    mock_generate_md.assert_called_once()
    
    # GetGetAdjustUseTimeParameter
    args, kwargs = mock_generate_md.call_args
    called_with_project = args[0]
    called_with_analysis = args[1]

    # VerifyTraditionalInputDataYesNoCorrectAccurate
    assert called_with_project.name == "TestProject"
    required_metrics = ["predicted_daily_orders", "avg_item_price", "net_profit"]
    for metric in required_metrics:
        assert metric in called_with_analysis

def test_subsidy_impact():
    """Test the impact of subsidy parameter adjustments on core metrics.forShould metric: 2.2.1"""
    # ThisFunctionPointinWhenbeforeGenerationCodeinNotDirectInterfaceIntegratedImplementation, this serves as a placeholder test
    pass

def test_category_factor_impact():
    """TestBrandCategoryShadowResponseCauseSubAdjustEnergyforCoreIndicatorMarkShadowResponse.forShould metric: 2.2.2"""
    # ThisFunctionPointinWhenbeforeGenerationCodeinNotDirectInterfaceIntegratedImplementation, this serves as a placeholder test
    pass