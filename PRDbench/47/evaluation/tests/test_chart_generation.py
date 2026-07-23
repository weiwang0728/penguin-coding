#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from utils.chart_generator import chart_generator
from config.settings import FILE_PATHS

def main():
 """TestBorrowingData VisualizationFunction"""
 print("TestBorrowingData VisualizationFunction...")
 
 # StandardPrepareTest Data
 borrow_data = {"DesignCalculateMachine": 15, "TextOptics": 8, "historical": 5, "Optics": 12}
 category_data = {"DesignCalculateMachine": 45, "TextOptics": 30, "historical": 15, "Optics": 10}
 
 try:
 # Generatebar_chart_path = chart_generator.generate_bar_chart(
 data=borrow_data,
 title="BookBorrowingSystemDesign",
 xlabel="BookClassification",
 ylabel="BorrowingTimesNumber",
 filename="borrow_statistics_bar.png"
 )
 
 # Generatepie_chart_path = chart_generator.generate_pie_chart(
 data=category_data,
 title="BookClassificationDivideDistribution",
 filename="category_distribution_pie.png"
 )
 
 # CheckFileYesNoGenerate
 charts_generated = []
 if bar_chart_path and os.path.exists(bar_chart_path):
 print(f"+ GenerateSuccess: {bar_chart_path}")
 charts_generated.append("")
 
 if pie_chart_path and os.path.exists(pie_chart_path):
 print(f"+ GenerateSuccess: {pie_chart_path}")
 charts_generated.append("")
 
 if len(charts_generated) >= 2:
 print(f"+ SuccessGenerate{len(charts_generated)}TypeCategoryTable")
 return True
 else:
 print(f"- Generate{len(charts_generated)}TypeTable，few2Type")
 return False
 
 except Exception as e:
 print(f"- TableGenerateAbnormal: {e}")
 return False

if __name__ == "__main__":
 success = main()
 sys.exit(0 if success else 1)
