#!/usr/bin/env python3
"""
Generate Histogram Test Script
"""

import sys
import os
import matplotlib.pyplot as plt
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

def generate_histogram():
    """Generate skill score histogram"""
    try:
        # Mock skill score data
        np.random.seed(42)  # Ensure reproducible results

        # Generate score data for four skill dimensions
        leadership_scores = np.random.normal(4.0, 0.6, 100)
        planning_scores = np.random.normal(3.8, 0.5, 100)
        decision_scores = np.random.normal(3.9, 0.7, 100)
        professional_scores = np.random.normal(4.1, 0.4, 100)

        # Limit scores to 1-5 range
        leadership_scores = np.clip(leadership_scores, 1, 5)
        planning_scores = np.clip(planning_scores, 1, 5)
        decision_scores = np.clip(decision_scores, 1, 5)
        professional_scores = np.clip(professional_scores, 1, 5)

        # Create 2x2 subplots
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Management Skills Score Distribution Histogram', fontsize=16, fontweight='bold')

        # Set Chinese font
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

        # Draw histogram for four skill dimensions
        skills_data = [
            (leadership_scores, 'Leadership & Motivation Skills', 'skyblue'),
            (planning_scores, 'Planning, Organization & Coordination Skills', 'lightgreen'),
            (decision_scores, 'Decision & Innovation Skills', 'orange'),
            (professional_scores, 'Professional & Control Skills', 'pink')
        ]

        for i, (scores, title, color) in enumerate(skills_data):
            row = i // 2
            col = i % 2

            axes[row, col].hist(scores, bins=20, alpha=0.7, color=color, edgecolor='black')
            axes[row, col].set_title(title, fontweight='bold')
            axes[row, col].set_xlabel('Score')
            axes[row, col].set_ylabel('Frequency')
            axes[row, col].grid(True, alpha=0.3)

            # Add statistics
            mean_score = np.mean(scores)
            std_score = np.std(scores)
            axes[row, col].axvline(mean_score, color='red', linestyle='--',
                                 label=f'Mean: {mean_score:.2f}')
            axes[row, col].legend()

        plt.tight_layout()

        # Save chart
        output_path = 'evaluation/test_histogram.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✅ Histogram generated: {output_path}")

        # Verify file exists
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"   File size: {file_size} bytes")
            return True
        else:
            print("❌ Histogram generation failed")
            return False

    except Exception as e:
        print(f"❌ Error generating histogram: {str(e)}")
        return False

if __name__ == "__main__":
    success = generate_histogram()
    sys.exit(0 if success else 1)
