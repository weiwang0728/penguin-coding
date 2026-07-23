#!/usr/bin/env python3
"""
Test SVG Format Chart Export Function
"""

import sys
import os
import matplotlib.pyplot as plt
import numpy as np
from math import pi
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

def export_chart_svg():
    """Export SVG format chart"""
    try:
        # Set Chinese font
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

        # Mock skill score data
        skills = ['Leadership & Motivation', 'Planning & Organization', 'Decision & Innovation', 'Professional Control']
        scores = [4.2, 3.9, 4.1, 4.0]

        # Calculate radar chart angles
        angles = [n / float(len(skills)) * 2 * pi for n in range(len(skills))]
        angles += angles[:1]  # Close the shape
        scores_closed = scores + scores[:1]  # Close data

        # Create radar chart
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))

        # Draw radar chart
        ax.plot(angles, scores_closed, 'o-', linewidth=3, label='Skill Score',
               color='#FF6B6B', marker='o', markersize=10)
        ax.fill(angles, scores_closed, alpha=0.25, color='#FF6B6B')

        # Set labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(skills, fontsize=12)

        # Set y-axis range and labels
        ax.set_ylim(0, 5)
        ax.set_yticks([1, 2, 3, 4, 5])
        ax.set_yticklabels(['1', '2', '3', '4', '5'], fontsize=10)
        ax.grid(True)

        # Add value labels
        for angle, score, skill in zip(angles[:-1], scores, skills):
            ax.text(angle, score + 0.1, f'{score:.1f}',
                   horizontalalignment='center', fontweight='bold')

        # Add title
        plt.title('Management Skills Radar Chart', size=16, fontweight='bold', pad=30)

        # Save as SVG format
        output_path = 'evaluation/test_chart.svg'
        plt.savefig(output_path, format='svg', bbox_inches='tight')
        plt.close()

        print(f"✅ SVG format chart exported: {output_path}")

        # Verify file exists and format is correct
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"   File size: {file_size} bytes")

            # Check file extension
            assert output_path.endswith('.svg')

            # Check file is not empty
            assert file_size > 0

            # Verify SVG file content (simple check)
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert '<svg' in content  # SVG file should contain svg tag
                assert '</svg>' in content
                assert 'polygon' in content or 'path' in content  # Should contain shape elements

            print("   SVG file verification passed")
            return True
        else:
            print("❌ SVG file generation failed")
            return False

    except Exception as e:
        print(f"❌ Error exporting SVG chart: {str(e)}")
        return False

if __name__ == "__main__":
    success = export_chart_svg()
    sys.exit(0 if success else 1)
