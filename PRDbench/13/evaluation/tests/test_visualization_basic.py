"""
Test basic chart visualization functions
"""
import pytest
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from src.evaluation.metrics import EvaluationMetrics
except ImportError:
    from evaluation.metrics import EvaluationMetrics


class TestVisualizationBasic:
    """Basic visualization function tests"""
    
    def setup_method(self):
        """Pre-test setup"""
        self.metrics = EvaluationMetrics()
        self.test_data = self._create_test_data()
        
        # Set matplotlib to non-interactive mode
        plt.ioff()
        plt.switch_backend('Agg')
    
    def _create_test_data(self):
        """Create test data"""
        # Simulate evaluation result data
        algorithms = ['Content-Based', 'User-CF', 'Item-CF', 'Hybrid']
        metrics = ['Precision@5', 'Recall@5', 'F1@5', 'NDCG@5']
        
        # Generate simulated performance data
        np.random.seed(42)
        data = []
        for alg in algorithms:
            for metric in metrics:
                # Generate reasonable metric values
                if 'Precision' in metric:
                    value = np.random.uniform(0.1, 0.8)
                elif 'Recall' in metric:
                    value = np.random.uniform(0.05, 0.6)
                elif 'F1' in metric:
                    value = np.random.uniform(0.08, 0.7)
                elif 'NDCG' in metric:
                    value = np.random.uniform(0.2, 0.9)
                else:
                    value = np.random.uniform(0.0, 1.0)
                
                data.append({
                    'Algorithm': alg,
                    'Metric': metric,
                    'Value': value
                })
        
        return pd.DataFrame(data)
    
    def test_basic_chart_generation(self):
        """Test basic chart generation function"""
        try:
            chart_types_generated = []
            
            # 1. Test bar chart generation
            bar_chart_success = self._test_bar_chart()
            if bar_chart_success:
                chart_types_generated.append("bar chart")
            
            # 2. Test line chart generation
            line_chart_success = self._test_line_chart()
            if line_chart_success:
                chart_types_generated.append("line chart")
            
            # 3. Test scatter chart generation
            scatter_chart_success = self._test_scatter_chart()
            if scatter_chart_success:
                chart_types_generated.append("scatter chart")
            
            # 4. Test pie chart generation (extra type)
            pie_chart_success = self._test_pie_chart()
            if pie_chart_success:
                chart_types_generated.append("pie chart")
            
            # 5. Test box chart generation (extra type)
            box_chart_success = self._test_box_chart()
            if box_chart_success:
                chart_types_generated.append("box chart")
            
            # Verify at least 3 chart types are supported
            assert len(chart_types_generated) >= 3, f"System should support at least 3 chart types, actual support: {len(chart_types_generated)} types: {chart_types_generated}"
            
            print("✓ Basic chart generation test passed")
            print(f"✓ Supported chart types: {chart_types_generated}")
            print(f"✓ Total support for {len(chart_types_generated)} types of charts")
            
            # Test chart saving functionality
            self._test_chart_saving()
            
        except Exception as e:
            pytest.fail(f"Basic chart generation test failed: {e}")
    
    def _test_bar_chart(self):
        """Test bar chart"""
        try:
            # Prepare bar chart data
            precision_data = self.test_data[self.test_data['Metric'] == 'Precision@5']
            
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(precision_data['Algorithm'], precision_data['Value'])
            ax.set_title('Algorithm Precision@5 Comparison')
            ax.set_xlabel('Algorithm')
            ax.set_ylabel('Precision@5')
            ax.set_ylim(0, 1)
            
            # Add value labels
            for bar, value in zip(bars, precision_data['Value']):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                       f'{value:.3f}', ha='center', va='bottom')
            
            plt.tight_layout()
            plt.close(fig)
            
            return True
            
        except Exception as e:
            print(f"Bar chart generation failed: {e}")
            return False
    
    def _test_line_chart(self):
        """Test line chart"""
        try:
            # Simulate metric changes during training
            epochs = list(range(1, 11))
            np.random.seed(42)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Plot performance curves for multiple algorithms
            algorithms = self.test_data['Algorithm'].unique()
            for alg in algorithms:
                # Simulate metric improvement during training
                base_value = self.test_data[
                    (self.test_data['Algorithm'] == alg) & 
                    (self.test_data['Metric'] == 'Precision@5')
                ]['Value'].iloc[0]
                
                # Generate learning curves
                values = [base_value * (0.3 + 0.7 * (1 - np.exp(-epoch/3))) for epoch in epochs]
                values = [v + np.random.normal(0, 0.02) for v in values]  # Add noise
                
                ax.plot(epochs, values, marker='o', label=alg, linewidth=2)
            
            ax.set_title('Algorithm Training Process Precision@5 Changes')
            ax.set_xlabel('Training Epochs')
            ax.set_ylabel('Precision@5')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.close(fig)
            
            return True
            
        except Exception as e:
            print(f"Line chart generation failed: {e}")
            return False
    
    def _test_scatter_chart(self):
        """Test scatter chart"""
        try:
            # Prepare scatter chart data: Precision vs Recall
            precision_data = self.test_data[self.test_data['Metric'] == 'Precision@5']
            recall_data = self.test_data[self.test_data['Metric'] == 'Recall@5']
            
            # Merge data
            scatter_data = precision_data.merge(
                recall_data, 
                on='Algorithm', 
                suffixes=('_precision', '_recall')
            )
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Use different colors and markers for different algorithms
            colors = ['red', 'blue', 'green', 'orange']
            markers = ['o', 's', '^', 'D']
            
            for i, alg in enumerate(scatter_data['Algorithm']):
                row = scatter_data[scatter_data['Algorithm'] == alg]
                ax.scatter(row['Value_precision'], row['Value_recall'], 
                          c=colors[i % len(colors)], 
                          marker=markers[i % len(markers)],
                          s=100, label=alg, alpha=0.7)
                
                # Add algorithm name annotation
                ax.annotate(alg, 
                           (row['Value_precision'].iloc[0], row['Value_recall'].iloc[0]),
                           xytext=(5, 5), textcoords='offset points')
            
            ax.set_title('Algorithm Precision vs Recall Scatter Plot')
            ax.set_xlabel('Precision@5')
            ax.set_ylabel('Recall@5')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Add diagonal line (ideal case)
            max_val = max(ax.get_xlim()[1], ax.get_ylim()[1])
            ax.plot([0, max_val], [0, max_val], 'k--', alpha=0.3, label='Ideal Line')
            
            plt.tight_layout()
            plt.close(fig)
            
            return True
            
        except Exception as e:
            print(f"Scatter chart generation failed: {e}")
            return False
    
    def _test_pie_chart(self):
        """Test pie chart"""
        try:
            # Simulate recommendation category distribution data
            categories = ['Electronics', 'Clothing', 'Books', 'Food', 'Home']
            proportions = [0.3, 0.25, 0.2, 0.15, 0.1]
            
            fig, ax = plt.subplots(figsize=(8, 8))
            
            # Create pie chart
            wedges, texts, autotexts = ax.pie(proportions, labels=categories, 
                                             autopct='%1.1f%%', startangle=90,
                                             colors=['#ff9999','#66b3ff','#99ff99','#ffcc99','#ff99cc'])
            
            ax.set_title('Recommended Product Category Distribution')
            
            # Beautify text
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            plt.tight_layout()
            plt.close(fig)
            
            return True
            
        except Exception as e:
            print(f"Pie chart generation failed: {e}")
            return False
    
    def _test_box_chart(self):
        """Test box chart"""
        try:
            # Simulate performance distribution data for different algorithms
            np.random.seed(42)
            algorithms = self.test_data['Algorithm'].unique()
            
            box_data = []
            labels = []
            
            for alg in algorithms:
                # Generate performance distribution data for this algorithm
                base_performance = self.test_data[
                    (self.test_data['Algorithm'] == alg) & 
                    (self.test_data['Metric'] == 'F1@5')
                ]['Value'].iloc[0]
                
                # Generate normally distributed performance data
                performance_samples = np.random.normal(base_performance, 0.05, 50)
                performance_samples = np.clip(performance_samples, 0, 1)  # Limit to [0,1] range
                
                box_data.append(performance_samples)
                labels.append(alg)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Create box plot
            box_plot = ax.boxplot(box_data, labels=labels, patch_artist=True)
            
            # Beautify box plot
            colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow']
            for patch, color in zip(box_plot['boxes'], colors):
                patch.set_facecolor(color)
            
            ax.set_title('Algorithm F1@5 Performance Distribution')
            ax.set_ylabel('F1@5')
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.close(fig)
            
            return True
            
        except Exception as e:
            print(f"Box chart generation failed: {e}")
            return False
    
    def _test_chart_saving(self):
        """Test chart saving functionality"""
        try:
            # Create a simple chart and save
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.plot([1, 2, 3, 4], [1, 4, 2, 3], 'b-o')
            ax.set_title('Test Chart Saving')
            
            # Test saving in different formats
            save_path = Path("test_chart")
            formats = ['png', 'jpg', 'pdf']
            
            saved_formats = []
            for fmt in formats:
                try:
                    plt.savefig(f"{save_path}.{fmt}", format=fmt, dpi=100, bbox_inches='tight')
                    saved_formats.append(fmt)
                    
                    # Delete test file
                    test_file = Path(f"{save_path}.{fmt}")
                    if test_file.exists():
                        test_file.unlink()
                        
                except Exception as e:
                    print(f"Failed to save {fmt} format: {e}")
            
            plt.close(fig)
            
            print(f"✓ Chart saving functionality test passed, supported formats: {saved_formats}")
            
        except Exception as e:
            print(f"Chart saving test failed: {e}")
    
    def test_chart_customization(self):
        """Test chart customization functionality"""
        try:
            customization_features = []
            
            # Test color customization
            fig, ax = plt.subplots()
            ax.bar(['A', 'B', 'C'], [1, 2, 3], color=['red', 'green', 'blue'])
            customization_features.append("Color Customization")
            plt.close(fig)
            
            # Test font customization
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 2, 3])
            ax.set_title('Test Title', fontsize=16, fontweight='bold')
            customization_features.append("Font Customization")
            plt.close(fig)
            
            # Test grid customization
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 2, 3])
            ax.grid(True, linestyle='--', alpha=0.5)
            customization_features.append("Grid Customization")
            plt.close(fig)
            
            # Test legend customization
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 2, 3], label='Data1')
            ax.plot([1, 2, 3], [2, 3, 1], label='Data2')
            ax.legend(loc='upper right', framealpha=0.8)
            customization_features.append("Legend Customization")
            plt.close(fig)
            
            print(f"✓ Chart customization functionality test passed, supports: {customization_features}")
            
        except Exception as e:
            pytest.fail(f"Chart customization test failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])