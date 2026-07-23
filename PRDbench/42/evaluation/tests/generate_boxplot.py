#!/usr/bin/env python3
"""
Generate Boxplot Test Script
"""

import sys
import os
import matplotlib.pyplot as plt
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

def generate_boxplot():
    """Generate skill score boxplot"""
    try:
        # Mock different management level skill score data
        np.random.seed(42)  # Ensure reproducible results

        # Generate data for different levels
        junior_data = {
            'leadership': np.random.normal(3.2, 0.4, 30),
            'planning': np.random.normal(3.4, 0.3, 30),
            'decision': np.random.normal(3.1, 0.5, 30),
            'professional': np.random.normal(3.3, 0.4, 30)
        }

        middle_data = {
            'leadership': np.random.normal(3.9, 0.3, 25),
            'planning': np.random.normal(4.0, 0.4, 25),
            'decision': np.random.normal(3.8, 0.3, 25),
            'professional': np.random.normal(4.1, 0.3, 25)
        }

        senior_data = {
            'leadership': np.random.normal(4.5, 0.3, 20),
            'planning': np.random.normal(4.4, 0.2, 20),
            'decision': np.random.normal(4.3, 0.4, 20),
            'professional': np.random.normal(4.6, 0.2, 20)
        }

        # Limit scores to 1-5 range
        for data_dict in [junior_data, middle_data, senior_data]:
            for skill in data_dict:
                data_dict[skill] = np.clip(data_dict[skill], 1, 5)

        # Create boxplot
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Skill Score Boxplot Comparison by Management Level', fontsize=16, fontweight='bold')

        # Set Chinese font
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

        # Skill dimension information
        skills_info = [
            ('leadership', 'Leadership & Motivation Skills'),
            ('planning', 'Planning, Organization & Coordination Skills'),
            ('decision', 'Decision & Innovation Skills'),
            ('professional', 'Professional & Control Skills')
        ]

        # Draw boxplot for each skill dimension
        for i, (skill_key, skill_name) in enumerate(skills_info):
            row = i // 2
            col = i % 2

            # Prepare data
            data_to_plot = [
                junior_data[skill_key],
                middle_data[skill_key],
                senior_data[skill_key]
            ]

            # Draw boxplot
            box_plot = axes[row, col].boxplot(data_to_plot,
                                            labels=['Junior', 'Middle', 'Senior'],
                                            patch_artist=True)

            # Set colors
            colors = ['lightblue', 'lightgreen', 'lightcoral']
            for patch, color in zip(box_plot['boxes'], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)

            axes[row, col].set_title(skill_name, fontweight='bold')
            axes[row, col].set_xlabel('Management Level')
            axes[row, col].set_ylabel('Skill Score')
            axes[row, col].grid(True, alpha=0.3)
            axes[row, col].set_ylim(1, 5)

        plt.tight_layout()

        # Save chart
        output_path = 'evaluation/test_boxplot.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✅ Boxplot generated: {output_path}")

        # Verify file exists
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"   File size: {file_size} bytes")

            # Verify data trend
            print("   Data verification:")
            for skill_key, skill_name in skills_info:
                junior_mean = np.mean(junior_data[skill_key])
                middle_mean = np.mean(middle_data[skill_key])
                senior_mean = np.mean(senior_data[skill_key])

                print(f"   {skill_name}: Junior({junior_mean:.2f}) < Middle({middle_mean:.2f}) < Senior({senior_mean:.2f})")

                # Verify increasing trend between levels
                assert junior_mean < middle_mean < senior_mean

            return True
        else:
            print("❌ Boxplot generation failed")
            return False

    except Exception as e:
        print(f"❌ Error generating boxplot: {str(e)}")
        return False

if __name__ == "__main__":
    success = generate_boxplot()
    sys.exit(0 if success else 1)
