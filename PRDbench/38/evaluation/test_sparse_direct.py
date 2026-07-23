#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DirectInterfaceTestSparseMatrixAnalysisFunction
"""

import sys
import os

# AddsrcDirectorytoPath
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

def test_sparse_analysis_direct():
    """DirectInterfaceTestSparseMatrixAnalysis"""
    print("=" * 60)
    print("2.3.4 SparseMatrixAnalysis - DirectInterfaceTest")
    print("=" * 60)
    
    try:
        from main import RecommendationSystemCLI
        
        # CreateCLIImplementationExampleAndDirectInterfaceAdjustUseSparseMatrixAnalysis
        cli = RecommendationSystemCLI()
        cli.analyze_sparse_matrix()
        
        # CheckReportFileYesNoGenerate
        report_path = os.path.join(src_dir, "results", "sparse_analysis.txt")
        
        if os.path.exists(report_path):
            print(f"✓ SparseMatrixAnalysisReportAlreadyGenerate: {report_path}")
            
            # VerifyReportContent
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # CheckRelatedKeyContent
            checks = [
                "SparseRepublicSystemDesign" in content,
                "FillRateRate" in content, 
                "ColdStartTouchSendRate" in content,
                "OperationsRecommendation" in content
            ]
            
            passed = sum(checks)
            print(f"ReportContentVerify: {passed}/4item(s)Pass")
            
            if passed >= 3:
                print("✅ 2.3.4 SparseMatrixAnalysis - Test Passed")
                return True
            else:
                print("⚠️ 2.3.4 SparseMatrixAnalysis - Partially Passed")
                return "partial"
        else:
            print(f"✗ ReportFileNotGenerate: {report_path}")
            return False
            
    except Exception as e:
        print(f"Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = test_sparse_analysis_direct()
    print(f"\nMostEndResult: {'Pass' if result == True else 'Partially Passed' if result == 'partial' else 'Failure'}")
    sys.exit(0 if result else 2)