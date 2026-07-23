#!/usr/bin/env python3
"""
Test PNG Format Chart Export Function
"""

import sys
import os
import matplotlib.pyplot as plt
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

def export_chart_png():
    """Export PNG format chart"""
    try:
        # Set Chinese font
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

        # Mock skill score data
        skills = ['Leadership & Motivation', 'Planning & Organization', 'Decision & Innovation', 'Professional Control']
        scores = [4.2, 3.9, 4.1, 4.0]

        # Create bar chart
        fig, ax = plt.subplots(figsize=(10, 6))

        bars = ax.bar(skills, scores, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])

        # Set chart style
        ax.set_title('Management Skills Score Analysis', fontsize=16, fontweight='bold', pad=20)
        ax.set_ylabel('Skill Score', fontsize=12)
        ax.set_ylim(0, 5)

        # Add value labels
        for bar, score in zip(bars, scores):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                   f'{score:.1f}', ha='center', va='bottom', fontweight='bold')

        # Add grid
        ax.grid(True, alpha=0.3, axis='y')

        # Set x-axis label rotation
        plt.xticks(rotation=45, ha='right')

        plt.tight_layout()

        # Save as PNG format
        output_path = 'evaluation/test_chart.png'
        plt.savefig(output_path, format='png', dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✅ PNG format chart exported: {output_path}")

        # Verify file exists and format is correct
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"   File size: {file_size} bytes")

            # Check file extension
            assert output_path.endswith('.png')

            # Check file is not empty
            assert file_size > 0

            print("   File verification passed")
            return True
        else:
            print("❌ PNG file generation failed")
            return False

    except Exception as e:
        print(f"❌ Error exporting PNG chart: {str(e)}")
        return False

if __name__ == "__main__":
    success = export_chart_png()
    sys.exit(0 if success else 1)
