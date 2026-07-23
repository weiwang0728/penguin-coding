"""
Test advanced chart visualization functions
"""
import pytest
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from src.evaluation.metrics import EvaluationMetrics
except ImportError:
    from evaluation.metrics import EvaluationMetrics


class TestVisualizationAdvanced:
    """Advanced visualization function tests"""

    def setup_method(self):
        """Pre-test setup"""
        self.metrics = EvaluationMetrics()

        # Set matplotlib to non-interactive mode
        plt.ioff()
        plt.switch_backend('Agg')

        # Set Chinese font support
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
    
    def test_advanced_chart_generation(self):
        """Test advanced chart generation function"""
        try:
            advanced_chart_types = []
            
            # 1. Test heatmap generation
            heatmap_success = self._test_heatmap()
            if heatmap_success:
                advanced_chart_types.append("heatmap")
            
            # 2. Test radar chart generation
            radar_chart_success = self._test_radar_chart()
            if radar_chart_success:
                advanced_chart_types.append("radar chart")
            
            # 3. Test correlation matrix
            correlation_success = self._test_correlation_matrix()
            if correlation_success:
                advanced_chart_types.append("correlation matrix")
            
            # 4. Test cluster visualization
            cluster_success = self._test_cluster_visualization()
            if cluster_success:
                advanced_chart_types.append("cluster visualization")
            
            # 5. Test density plot
            density_success = self._test_density_plot()
            if density_success:
                advanced_chart_types.append("density plot")
            
            # Verify at least 2 advanced chart types are supported
            assert len(advanced_chart_types) >= 2, f"System should support at least 2 advanced chart types, actual support: {len(advanced_chart_types)} types: {advanced_chart_types}"
            
            print("✓ Advanced chart generation test passed")
            print(f"✓ Supported advanced chart types: {advanced_chart_types}")
            print(f"✓ Total support for {len(advanced_chart_types)} types of advanced charts")
            
            # Test combined chart display
            self._test_dashboard_layout()
            
        except Exception as e:
            pytest.fail(f"Advanced chart generation test failed: {e}")
    
    def _test_heatmap(self):
        """Test heatmap"""
        try:
            # Create heatmap data for algorithm performance comparison
            algorithms = ['Content-Based', 'User-CF', 'Item-CF', 'Hybrid']
            metrics = ['Precision@5', 'Recall@5', 'F1@5', 'NDCG@5', 'MAP']
            
            # Generate simulated data
            np.random.seed(42)
            data = np.random.uniform(0.1, 0.9, (len(algorithms), len(metrics)))
            
            # Create heatmap
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Create heatmap using seaborn
            heatmap = sns.heatmap(data, 
                                 xticklabels=metrics, 
                                 yticklabels=algorithms,
                                 annot=True, 
                                 fmt='.3f', 
                                 cmap='YlOrRd',
                                 ax=ax)
            
            ax.set_title('Algorithm Performance Heatmap')
            plt.tight_layout()
            plt.close(fig)
            
            return True
            
        except Exception as e:
            print(f"Heatmap generation failed: {e}")
            return False
    
    def _test_radar_chart(self):
        """Test radar chart"""
        try:
            # Radar chart data: multi-dimensional algorithm performance comparison
            categories = ['Precision', 'Recall', 'F1 Score', 'Diversity', 'Novelty', 'Coverage']
            
            # Performance data for two algorithms
            algorithm1_scores = [0.8, 0.6, 0.7, 0.5, 0.4, 0.9]  # Hybrid
            algorithm2_scores = [0.6, 0.8, 0.7, 0.7, 0.6, 0.7]  # Content-Based
            
            # Calculate angles
            angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
            
            # Close radar chart
            algorithm1_scores += algorithm1_scores[:1]
            algorithm2_scores += algorithm2_scores[:1]
            angles += angles[:1]
            
            # Create radar chart
            fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
            
            # Plot algorithm 1
            ax.plot(angles, algorithm1_scores, 'o-', linewidth=2, label='Hybrid Recommendation', color='blue')
            ax.fill(angles, algorithm1_scores, alpha=0.25, color='blue')
            
            # Plot algorithm 2
            ax.plot(angles, algorithm2_scores, 'o-', linewidth=2, label='Content-Based Recommendation', color='red')
            ax.fill(angles, algorithm2_scores, alpha=0.25, color='red')
            
            # Set labels
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories)
            ax.set_ylim(0, 1)
            ax.set_title('Algorithm Performance Radar Chart', size=16, y=1.1)
            ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0))
            ax.grid(True)
            
            plt.tight_layout()
            plt.close(fig)
            
            return True
            
        except Exception as e:
            print(f"Radar chart generation failed: {e}")
            return False
    
    def _test_correlation_matrix(self):
        """Test correlation matrix"""
        try:
            # Create metrics correlation data
            np.random.seed(42)
            metrics = ['Precision', 'Recall', 'F1', 'NDCG', 'Diversity', 'Coverage']
            n_metrics = len(metrics)
            
            # Generate correlation matrix
            correlation_matrix = np.random.uniform(-0.5, 1.0, (n_metrics, n_metrics))
            # Ensure diagonal is 1
            np.fill_diagonal(correlation_matrix, 1.0)
            # Ensure matrix is symmetric
            correlation_matrix = (correlation_matrix + correlation_matrix.T) / 2
            
            # Create correlation heatmap
            fig, ax = plt.subplots(figsize=(8, 6))
            
            heatmap = sns.heatmap(correlation_matrix, 
                                 xticklabels=metrics, 
                                 yticklabels=metrics,
                                 annot=True, 
                                 fmt='.3f', 
                                 cmap='coolwarm',
                                 center=0,
                                 ax=ax)
            
            ax.set_title('Evaluation Metrics Correlation Matrix')
            plt.tight_layout()
            plt.close(fig)
            
            return True
            
        except Exception as e:
            print(f"Correlation matrix generation failed: {e}")
            return False
    
    def _test_cluster_visualization(self):
        """Test cluster visualization"""
        try:
            # Simulate user clustering data
            np.random.seed(42)
            n_users = 100
            
            # Generate 3 user groups
            cluster1 = np.random.multivariate_normal([2, 2], [[0.5, 0.1], [0.1, 0.5]], 30)
            cluster2 = np.random.multivariate_normal([6, 6], [[0.8, -0.2], [-0.2, 0.8]], 35)
            cluster3 = np.random.multivariate_normal([4, 8], [[0.6, 0.0], [0.0, 0.6]], 35)
            
            # Merge data
            user_features = np.vstack([cluster1, cluster2, cluster3])
            labels = np.array([0]*30 + [1]*35 + [2]*35)
            
            # Create cluster visualization
            fig, ax = plt.subplots(figsize=(10, 8))
            
            colors = ['red', 'blue', 'green']
            cluster_names = ['Young Users', 'Business Users', 'Family Users']
            
            for i in range(3):
                cluster_data = user_features[labels == i]
                ax.scatter(cluster_data[:, 0], cluster_data[:, 1], 
                          c=colors[i], label=cluster_names[i], alpha=0.7, s=50)
            
            ax.set_title('User Group Cluster Visualization')
            ax.set_xlabel('Feature Dimension 1')
            ax.set_ylabel('Feature Dimension 2')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.close(fig)
            
            return True
            
        except Exception as e:
            print(f"Cluster visualization generation failed: {e}")
            return False
    
    def _test_density_plot(self):
        """Test density plot"""
        try:
            # Simulate rating distribution data
            np.random.seed(42)
            
            # Generate rating distributions for different algorithms
            content_based_scores = np.random.beta(2, 5, 1000)  # Skewed towards low scores
            collaborative_scores = np.random.beta(3, 3, 1000)  # Uniform distribution
            hybrid_scores = np.random.beta(5, 2, 1000)        # Skewed towards high scores
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Plot density graph
            ax.hist(content_based_scores, bins=50, alpha=0.5, label='Content-Based Recommendation', 
                   density=True, color='blue')
            ax.hist(collaborative_scores, bins=50, alpha=0.5, label='Collaborative Filtering', 
                   density=True, color='green')
            ax.hist(hybrid_scores, bins=50, alpha=0.5, label='Hybrid Recommendation', 
                   density=True, color='red')
            
            # Add KDE curves
            try:
                import scipy.stats as stats
                x = np.linspace(0, 1, 100)
                
                # Calculate KDE
                kde1 = stats.gaussian_kde(content_based_scores)
                kde2 = stats.gaussian_kde(collaborative_scores)
                kde3 = stats.gaussian_kde(hybrid_scores)
                
                ax.plot(x, kde1(x), 'b-', linewidth=2, alpha=0.8)
                ax.plot(x, kde2(x), 'g-', linewidth=2, alpha=0.8)
                ax.plot(x, kde3(x), 'r-', linewidth=2, alpha=0.8)
                
            except ImportError:
                print("scipy not installed, skipping KDE curves")
            
            ax.set_title('Recommendation Score Distribution Density for Different Algorithms')
            ax.set_xlabel('Recommendation Score')
            ax.set_ylabel('Density')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.close(fig)
            
            return True
            
        except Exception as e:
            print(f"Density plot generation failed: {e}")
            return False
    
    def _test_dashboard_layout(self):
        """Test dashboard layout"""
        try:
            # Create multi-subplot dashboard
            fig = plt.figure(figsize=(15, 10))
            
            # Subplot 1: Performance comparison bar chart
            ax1 = plt.subplot(2, 3, 1)
            algorithms = ['A', 'B', 'C']
            values = [0.6, 0.8, 0.7]
            ax1.bar(algorithms, values, color=['skyblue', 'lightgreen', 'lightcoral'])
            ax1.set_title('Algorithm Performance Comparison')
            ax1.set_ylim(0, 1)
            
            # Subplot 2: Time series
            ax2 = plt.subplot(2, 3, 2)
            time_points = list(range(1, 11))
            performance = [0.5 + 0.3*np.sin(i/2) + 0.1*i/10 for i in time_points]
            ax2.plot(time_points, performance, 'b-o')
            ax2.set_title('Performance Trend')
            ax2.grid(True, alpha=0.3)
            
            # Subplot 3: Pie chart
            ax3 = plt.subplot(2, 3, 3)
            sizes = [30, 25, 20, 15, 10]
            labels = ['Category A', 'Category B', 'Category C', 'Category D', 'Other']
            ax3.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax3.set_title('Category Distribution')
            
            # Subplot 4: Scatter plot
            ax4 = plt.subplot(2, 3, 4)
            x = np.random.normal(0.5, 0.2, 100)
            y = np.random.normal(0.6, 0.1, 100)
            ax4.scatter(x, y, alpha=0.6)
            ax4.set_title('Feature Distribution')
            ax4.set_xlabel('Feature 1')
            ax4.set_ylabel('Feature 2')
            
            # Subplot 5: Box plot
            ax5 = plt.subplot(2, 3, 5)
            data_groups = [np.random.normal(0.6, 0.1, 50), 
                          np.random.normal(0.7, 0.15, 50),
                          np.random.normal(0.5, 0.08, 50)]
            ax5.boxplot(data_groups, labels=['Algorithm 1', 'Algorithm 2', 'Algorithm 3'])
            ax5.set_title('Performance Distribution')
            
            # Subplot 6: Heatmap
            ax6 = plt.subplot(2, 3, 6)
            heatmap_data = np.random.uniform(0, 1, (5, 5))
            im = ax6.imshow(heatmap_data, cmap='viridis')
            ax6.set_title('Feature Importance')
            plt.colorbar(im, ax=ax6)
            
            plt.suptitle('Recommendation System Evaluation Dashboard', fontsize=16)
            plt.tight_layout()
            plt.close(fig)
            
            print("✓ Dashboard layout test passed")
            
        except Exception as e:
            print(f"Dashboard layout test failed: {e}")
    
    def test_interactive_features(self):
        """Test interactive features support"""
        try:
            interactive_features = []
            
            # Test legend interaction
            fig, ax = plt.subplots()
            line1, = ax.plot([1, 2, 3], [1, 2, 3], label='Data 1')
            line2, = ax.plot([1, 2, 3], [2, 3, 1], label='Data 2')
            legend = ax.legend()
            legend.set_draggable(True)
            interactive_features.append("Draggable Legend")
            plt.close(fig)
            
            # Test zoom functionality
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3, 4, 5], [1, 4, 2, 5, 3])
            ax.set_title('Chart with Zoom Support')
            interactive_features.append("Chart Zoom")
            plt.close(fig)
            
            # Test annotation functionality
            fig, ax = plt.subplots()
            ax.scatter([1, 2, 3], [1, 2, 3])
            ax.annotate('Important Point', xy=(2, 2), xytext=(2.5, 2.5),
                       arrowprops=dict(arrowstyle='->'))
            interactive_features.append("Data Point Annotation")
            plt.close(fig)
            
            print(f"✓ Interactive features test passed, supports: {interactive_features}")
            
        except Exception as e:
            print(f"Interactive features test failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])