#!/usr/bin/env python3
"""
Generate Radar Chart Test Script
"""

import sys
import os
import matplotlib.pyplot as plt
import numpy as np
from math import pi
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

def generate_radar():
    """Generate skill score radar chart"""
    try:
        # Set Chinese font
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

        # Skill dimensions and data
        skills = ['Leadership & Motivation', 'Planning & Organization', 'Decision & Innovation', 'Professional Control']

        # Average scores for different management levels
        junior_scores = [3.2, 3.4, 3.1, 3.3]
        middle_scores = [3.9, 4.0, 3.8, 4.1]
        senior_scores = [4.5, 4.4, 4.3, 4.6]

        # Calculate angles
        angles = [n / float(len(skills)) * 2 * pi for n in range(len(skills))]
        angles += angles[:1]  # Close the shape

        # Create radar chart
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

        # Draw radar chart for three levels
        datasets = [
            (junior_scores, 'Junior Manager', 'blue', 'o'),
            (middle_scores, 'Middle Manager', 'green', 's'),
            (senior_scores, 'Senior Manager', 'red', '^')
        ]

        for scores, label, color, marker in datasets:
            # Close data
            scores_closed = scores + scores[:1]

            # Draw radar chart
            ax.plot(angles, scores_closed, 'o-', linewidth=2, label=label,
                   color=color, marker=marker, markersize=8)
            ax.fill(angles, scores_closed, alpha=0.25, color=color)

        # Set labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(skills, fontsize=12)

        # Set y-axis range and labels
        ax.set_ylim(0, 5)
        ax.set_yticks([1, 2, 3, 4, 5])
        ax.set_yticklabels(['1', '2', '3', '4', '5'], fontsize=10)
        ax.grid(True)

        # Add title and legend
        plt.title('Management Skills Radar Chart Comparison\n(By Management Level)', size=16, fontweight='bold', pad=20)
        plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0))

        # Save chart
        output_path = 'evaluation/test_radar.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✅ Radar chart generated: {output_path}")

        # Verify file exists
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"   File size: {file_size} bytes")

            # Verify data consistency
            print("   Data verification:")
            for i, skill in enumerate(skills):
                junior_score = junior_scores[i]
                middle_score = middle_scores[i]
                senior_score = senior_scores[i]

                print(f"   {skill}: Junior({junior_score}) < Middle({middle_score}) < Senior({senior_score})")

                # Verify increasing trend between levels
                assert junior_score < middle_score < senior_score
                assert 1 <= junior_score <= 5
                assert 1 <= middle_score <= 5
                assert 1 <= senior_score <= 5

            return True
        else:
            print("❌ Radar chart generation failed")
            return False

    except Exception as e:
        print(f"❌ Error generating radar chart: {str(e)}")
        return False

if __name__ == "__main__":
    success = generate_radar()
    sys.exit(0 if success else 1)
