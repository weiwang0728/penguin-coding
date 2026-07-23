"""
Visualization Functional Test
"""
import pytest
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from visualization import Visualizer
from scale_manager import ScaleManager
from data_manager import DataManager
from models import create_tables

@pytest.fixture
def setup_visualization_test():
    """Set up visualization test environment"""
    create_tables()

    scale_manager = ScaleManager()
    data_manager = DataManager()
    visualizer = Visualizer()

    # Create default scales
    scale_manager.create_default_scales()

    # Create test data
    participants_data = [
        {'participant_id': 'VIZ_001', 'gender': 'Male', 'age': 20, 'grade': 'Sophomore'},
        {'participant_id': 'VIZ_002', 'gender': 'Female', 'age': 19, 'grade': 'Freshman'},
        {'participant_id': 'VIZ_003', 'gender': 'Male', 'age': 21, 'grade': 'Junior'},
        {'participant_id': 'VIZ_004', 'gender': 'Female', 'age': 20, 'grade': 'Sophomore'},
    ]

    for p_data in participants_data:
        data_manager.create_participant(**p_data)

    # Create questionnaire responses
    responses_data = [
        {'participant_id': 'VIZ_001', 'scale_id': 1, 'responses_data': {str(i): i % 5 + 3 for i in range(1, 9)}},
        {'participant_id': 'VIZ_002', 'scale_id': 1, 'responses_data': {str(i): (i + 2) % 5 + 3 for i in range(1, 9)}},
        {'participant_id': 'VIZ_003', 'scale_id': 1, 'responses_data': {str(i): (i + 4) % 5 + 3 for i in range(1, 9)}},
        {'participant_id': 'VIZ_004', 'scale_id': 1, 'responses_data': {str(i): (i + 1) % 5 + 3 for i in range(1, 9)}},
    ]

    for r_data in responses_data:
        data_manager.create_response(**r_data)

    return visualizer, scale_manager, data_manager

def test_export_chart_pdf(setup_visualization_test):
    """Test export chart in PDF format"""
    visualizer, scale_manager, data_manager = setup_visualization_test

    # Generate descriptive statistics chart
    result = visualizer.plot_descriptive_stats(scale_id=1)

    # Assert basic result
    assert 'error' not in result, f"Chart generation failed: {result.get('error', '')}"
    assert 'success' in result, "Missing success flag"
    assert result['success'] == True, "Chart generation not successful"

    # Test PDF export function
    if 'file_path' in result:
        original_path = Path(result['file_path'])
        pdf_path = original_path.with_suffix('.pdf')

        # Simulate PDF export
        export_result = visualizer.export_chart_as_pdf(original_path, pdf_path)

        # Assert
        assert export_result.get('success') == True, "PDF export failed"
        assert 'file_path' in export_result, "Missing PDF file path"

        # Clean up test files
        if pdf_path.exists():
            pdf_path.unlink()
        if original_path.exists():
            original_path.unlink()

def test_export_chart_svg(setup_visualization_test):
    """Test export chart in SVG format"""
    visualizer, scale_manager, data_manager = setup_visualization_test

    # Generate descriptive statistics chart
    result = visualizer.plot_descriptive_stats(1)

    # Assert basic result
    assert 'error' not in result, f"Heatmap generation failed: {result.get('error', '')}"
    assert 'success' in result, "Missing success flag"

    # Test SVG export function
    if result.get('success') and 'file_path' in result:
        original_path = Path(result['file_path'])
        svg_path = original_path.with_suffix('.svg')

        # Simulate SVG export
        export_result = visualizer.export_chart_as_svg(original_path, svg_path)

        # Assert
        assert export_result.get('success') == True, "SVG export failed"
        assert 'file_path' in export_result, "Missing SVG file path"

        # Verify SVG file characteristics
        if svg_path.exists():
            with open(svg_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert '<svg' in content, "SVG file format incorrect"
                assert '</svg>' in content, "SVG file format incomplete"

        # Clean up test files
        if svg_path.exists():
            svg_path.unlink()
        if original_path.exists():
            original_path.unlink()

def test_plot_descriptive_stats(setup_visualization_test):
    """Test descriptive statistics chart generation"""
    visualizer, scale_manager, data_manager = setup_visualization_test

    # Generate descriptive statistics chart
    result = visualizer.plot_descriptive_stats(scale_id=1)

    # Assert
    assert 'error' not in result, f"Descriptive statistics chart generation failed: {result.get('error', '')}"
    assert 'success' in result, "Missing success flag"
    assert result['success'] == True, "Chart generation not successful"
    assert 'file_path' in result, "Missing file path"
    assert 'chart_type' in result, "Missing chart type"

    # Verify file exists
    if 'file_path' in result:
        file_path = Path(result['file_path'])
        assert file_path.exists(), f"Chart file does not exist: {file_path}"
        assert file_path.suffix in ['.png', '.jpg', '.jpeg', '.pdf'], "Chart file format incorrect"

        # Clean up test file
        if file_path.exists():
            file_path.unlink()

def test_plot_correlation_heatmap(setup_visualization_test):
    """Test correlation analysis heatmap generation"""
    visualizer, scale_manager, data_manager = setup_visualization_test

    # Generate correlation analysis heatmap
    result = visualizer.plot_correlation_heatmap(scale_ids=[1])

    # Assert
    assert 'error' not in result, f"Correlation heatmap generation failed: {result.get('error', '')}"
    assert 'success' in result, "Missing success flag"

    if result.get('success'):
        assert 'file_path' in result, "Missing file path"
        assert 'chart_type' in result, "Missing chart type"
        assert result['chart_type'] == 'correlation_heatmap', "Chart type does not match"

        # Verify file exists
        file_path = Path(result['file_path'])
        assert file_path.exists(), f"Heatmap file does not exist: {file_path}"

        # Clean up test file
        if file_path.exists():
            file_path.unlink()

def test_plot_group_comparison(setup_visualization_test):
    """Test group comparison chart generation"""
    visualizer, scale_manager, data_manager = setup_visualization_test

    # Generate group comparison chart
    result = visualizer.plot_group_comparison(scale_id=1, group_by='gender')

    # Assert
    assert 'error' not in result, f"Group comparison chart generation failed: {result.get('error', '')}"
    assert 'success' in result, "Missing success flag"

    if result.get('success'):
        assert 'file_path' in result, "Missing file path"
        assert 'chart_type' in result, "Missing chart type"
        assert result['chart_type'] == 'group_comparison', "Chart type does not match"

        # Verify file exists
        file_path = Path(result['file_path'])
        assert file_path.exists(), f"Group comparison chart file does not exist: {file_path}"

        # Clean up test file
        if file_path.exists():
            file_path.unlink()

def test_create_interactive_dashboard(setup_visualization_test):
    """Test create interactive dashboard"""
    visualizer, scale_manager, data_manager = setup_visualization_test

    # Create interactive dashboard
    result = visualizer.create_interactive_dashboard(scale_id=1)

    # Assert
    assert 'error' not in result, f"Interactive dashboard creation failed: {result.get('error', '')}"
    assert 'success' in result, "Missing success flag"

    if result.get('success'):
        assert 'file_path' in result, "Missing file path"
        assert 'dashboard_type' in result, "Missing dashboard type"

        # Verify HTML file exists
        file_path = Path(result['file_path'])
        assert file_path.exists(), f"Dashboard file does not exist: {file_path}"
        assert file_path.suffix == '.html', "Dashboard file should be HTML format"

        # Verify HTML content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert '<html' in content.lower(), "HTML file format incorrect"
            assert '</html>' in content.lower(), "HTML file format incomplete"
            assert 'plotly' in content.lower() or 'chart' in content.lower(), "Dashboard should contain chart content"

        # Clean up test file
        if file_path.exists():
            file_path.unlink()

def test_plot_factor_analysis(setup_visualization_test):
    """Test factor analysis chart generation"""
    visualizer, scale_manager, data_manager = setup_visualization_test

    # Generate factor analysis chart
    result = visualizer.plot_factor_analysis(scale_id=1, n_factors=2)

    # Assert
    assert 'error' not in result, f"Factor analysis chart generation failed: {result.get('error', '')}"
    assert 'success' in result, "Missing success flag"

    if result.get('success'):
        assert 'file_path' in result, "Missing file path"
        assert 'chart_type' in result, "Missing chart type"
        assert result['chart_type'] == 'factor_analysis', "Chart type does not match"

        # Verify file exists
        file_path = Path(result['file_path'])
        assert file_path.exists(), f"Factor analysis chart file does not exist: {file_path}"

        # Clean up test file
        if file_path.exists():
            file_path.unlink()

def test_plot_path_analysis(setup_visualization_test):
    """Test path analysis chart generation"""
    visualizer, scale_manager, data_manager = setup_visualization_test

    # Define simple path model
    path_model = {
        'paths': [
            {'from': 'scale_1_total', 'to': 'scale_1_dim1', 'coefficient': 0.8},
            {'from': 'scale_1_total', 'to': 'scale_1_dim2', 'coefficient': 0.7}
        ],
        'variables': ['scale_1_total', 'scale_1_dim1', 'scale_1_dim2']
    }

    # Generate path analysis chart
    result = visualizer.plot_path_analysis(path_model)

    # Assert
    assert 'error' not in result, f"Path analysis chart generation failed: {result.get('error', '')}"
    assert 'success' in result, "Missing success flag"

    if result.get('success'):
        assert 'file_path' in result, "Missing file path"
        assert 'chart_type' in result, "Missing chart type"
        assert result['chart_type'] == 'path_analysis', "Chart type does not match"

        # Verify file exists
        file_path = Path(result['file_path'])
        assert file_path.exists(), f"Path analysis chart file does not exist: {file_path}"

        # Clean up test file
        if file_path.exists():
            file_path.unlink()

def test_chart_customization(setup_visualization_test):
    """Test chart customization options"""
    visualizer, scale_manager, data_manager = setup_visualization_test

    # Test customization options
    custom_options = {
        'title': 'Custom Title',
        'width': 800,
        'height': 600,
        'dpi': 300,
        'color_palette': 'viridis',
        'font_size': 12
    }

    # Generate chart with custom options
    result = visualizer.plot_descriptive_stats(scale_id=1, **custom_options)

    # Assert
    assert 'error' not in result, f"Custom chart generation failed: {result.get('error', '')}"
    assert 'success' in result, "Missing success flag"

    if result.get('success'):
        assert 'file_path' in result, "Missing file path"
        assert 'options_used' in result, "Missing options information"

        # Verify custom options were applied
        options_used = result['options_used']
        assert options_used.get('title') == 'Custom Title', "Title customization not applied"
        assert options_used.get('width') == 800, "Width customization not applied"
        assert options_used.get('height') == 600, "Height customization not applied"

        # Clean up test file
        file_path = Path(result['file_path'])
        if file_path.exists():
            file_path.unlink()

def test_batch_chart_generation(setup_visualization_test):
    """Test batch chart generation"""
    visualest_batch_chart_generation(setup_visualization_test):
    """Test batch chart generation"""
    viizer, scale_manager, data_manager = setup_visualization_test

    # Define batch generation tasks
    chart_tasks = [
        {'type': 'descriptive_stats', 'scale_id': 1},
        {'type': 'correlation_heatmap', 'scale_ids': [1]},
        {'type': 'group_comparison', 'scale_id': 1, 'group_by': 'gender'}
    ]

    # Execute batch generation
    results = visualizer.generate_charts_batch(chart_tasks)

    # Assert
    assert len(results) == len(chart_tasks), f"Generated chart quantity does not match, expected: {len(chart_tasks)}, actual: {len(results)}"

    # Verify each result
    for i, result in enumerate(results):
        assert 'task_index' in result, f"Result {i+1} missing task index"
        assert 'success' in result, f"Result {i+1} missing success flag"

        if result.get('success'):
            assert 'file_path' in result, f"Result {i+1} missing file path"

            # Clean up test file
            file_path = Path(result['file_path'])
            if file_path.exists():
                file_path.unlink()

def test_chart_format_support(setup_visualization_test):
    """Test chart format support"""
    visualizer, scale_manager, data_manager = setup_visualization_test

    # Test chart generation in different formats
    formats = ['png', 'pdf', 'svg', 'jpg']

    for fmt in formats:
        result = visualizer.plot_descriptive_stats(scale_id=1, output_format=fmt)

        # Assert
        assert 'error' not in result, f"{fmt} format chart generation failed: {result.get('error', '')}"

        if result.get('success'):
            assert 'file_path' in result, f"{fmt} format missing file path"

            file_path = Path(result['file_path'])
            assert file_path.suffix.lower() == f'.{fmt}', f"{fmt} format file extension incorrect"

            if file_path.exists():
                assert file_path.stat().st_size > 0, f"{fmt} format file size is 0"

                # Clean up test file
                file_path.unlink()

def test_visualization_error_handling(setup_visualization_test):
    """Test visualization error handling"""
    visualizer, scale_manager, data_manager = setup_visualization_test

    # Test non-existent scale ID
    result = visualizer.plot_descriptive_stats(scale_id=999)
    assert 'error' in result, "Should return error information"
    assert result['success'] == False, "Success flag should be False"

    # Test empty data
    # Create scale with no response data
    empty_scale = scale_manager.create_scale(name="Empty Scale", description="Scale with no data")
    result = visualizer.plot_descriptive_stats(scale_id=empty_scale.id)
    assert 'error' in result, "Empty data should return error information"

    # Test invalid grouping field
    result = visualizer.plot_group_comparison(scale_id=1, group_by='nonexistent_field')
    assert 'error' in result, "Invalid grouping field should return error information"
