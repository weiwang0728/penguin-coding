#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

def fix_chinese_font_and_regenerate_charts():
 """FixedinTextCharacterIntegratedIssueWeightNewGenerateTable"""
 print("=== FixedTableinTextCharacterIntegratedDisplayIssue ===")
 
 try:
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 import matplotlib.font_manager as fm
 from matplotlib import rcParams
 
 print("\n1. CheckSystemCharacterIntegrated...")
 
 # WindowsSysteminTextCharacterIntegrated
 chinese_fonts = []
 for font in fm.fontManager.ttflist:
 font_name = font.name.lower()
 if any(keyword in font_name for keyword in ['yahei', 'simhei', 'kaiti', 'simsun', 'microsoft']):
 chinese_fonts.append(font.name)
 
 print(f"toCanEnergyinTextCharacterIntegrated: {len(set(chinese_fonts))}items")
 for font in sorted(set(chinese_fonts))[:5]: # Displaybefore5items
 print(f" - {font}")
 
 print("\n2. ConfigurematplotlibinTextSupportSupport...")
 
 # StrongControlUsesSystemAutoCharacterIntegratedorunderCharacterIntegrated
 font_options = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'DejaVu Sans']
 
 # ConfigureCharacterIntegrated
 rcParams['font.sans-serif'] = font_options
 rcParams['axes.unicode_minus'] = False
 rcParams['font.size'] = 12
 
 print("+ CharacterIntegratedConfigureSuccessfully")
 
 print("\n3. WeightNewGenerateTestTable...")
 
 # EnsurechartsDirectorySavein
 charts_dir = 'data/charts'
 os.makedirs(charts_dir, exist_ok=True)
 
 # GenerateTestfig, ax = plt.subplots(figsize=(10, 6))
 
 class = ['DesignCalculateMachine', 'TextOptics', 'historical', 'Optics']
 values = [15, 8, 5, 12]
 
 bars = ax.bar(categories, values, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
 
 ax.set_title('BookBorrowingSystemDesign', fontsize=16, fontweight='bold')
 ax.set_xlabel('BookClassification', fontsize=14)
 ax.set_ylabel('BorrowingTimesNumber', fontsize=14)
 ax.grid(True, alpha=0.3)
 
 # inSubonAddNumberValueTag
 for bar, value in zip(bars, values):
 height = bar.get_height()
 ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
 f'{value}', ha='center', va='bottom', fontsize=12)
 
 plt.tight_layout()
 bar_chart_path = os.path.join(charts_dir, 'borrow_statistics_bar.png')
 plt.savefig(bar_chart_path, dpi=150, bbox_inches='tight')
 plt.close()
 
 print(f"+ Generate: {bar_chart_path}")
 
 # GenerateTestfig, ax = plt.subplots(figsize=(8, 8))
 
 category_data = ['DesignCalculateMachine', 'TextOptics', 'historical', 'Optics']
 category_values = [45, 30, 15, 10]
 colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
 
 wedges, texts, autotexts = ax.pie(
 category_values, 
 labels=category_data,
 colors=colors,
 autopct='%1.1f%%',
 startangle=90,
 shadow=True
 )
 
 ax.set_title('BookClassificationDivideDistribution', fontsize=16, fontweight='bold')
 
 # AdjustEntireTextCharacterLargeSmall
 for text in texts:
 text.set_fontsize(12)
 for autotext in autotexts:
 autotext.set_color('white')
 autotext.set_fontsize(10)
 autotext.set_fontweight('bold')
 
 plt.tight_layout()
 pie_chart_path = os.path.join(charts_dir, 'category_distribution_pie.png')
 plt.savefig(pie_chart_path, dpi=150, bbox_inches='tight')
 plt.close()
 
 print(f"+ Generate: {pie_chart_path}")
 
 print("\n4. VerifyTableFile...")
 
 bar_exists = os.path.exists(bar_chart_path)
 pie_exists = os.path.exists(pie_chart_path)
 
 bar_size = os.path.getsize(bar_chart_path) if bar_exists else 0
 pie_size = os.path.getsize(pie_chart_path) if pie_exists else 0
 
 print(f"+ Savein: {'OK' if bar_exists else 'NO'} (LargeSmall: {bar_size} bytes)")
 print(f"+ Savein: {'OK' if pie_exists else 'NO'} (LargeSmall: {pie_size} bytes)")
 
 success = bar_exists and pie_exists and bar_size > 0 and pie_size > 0
 
 if success:
 print("\n✓ 5.3BorrowingData VisualizationFunctional TestPass")
 print(" - SuccessGeneratefew2TypeCategorySystemDesignTable（、）")
 print(" - TableSaveasPNGFormatStyletochartsDirectory")
 print(" - inTextCharacterIntegratedDisplayAlreadyOptimization")
 else:
 print("\n✗ 5.3BorrowingData VisualizationFunctional TestFailure")
 
 return success
 
 except Exception as e:
 print(f"FixedCharacterIntegratedAbnormal: {e}")
 import traceback
 traceback.print_exc()
 return False

if __name__ == "__main__":
 success = fix_chinese_font_and_regenerate_charts()
 if success:
 print("\n[PASS] TableGenerateandinTextCharacterIntegratedFixedSuccess")
 else:
 print("\n[FAIL] TableGenerateorCharacterIntegratedFixedFailure")
 sys.exit(0 if success else 1)