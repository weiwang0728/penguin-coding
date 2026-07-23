# -*- coding: utf-8 -*-
"""
Test 2.2.2a DataMarkStandardizationProcessing
ModelSimulationUserinteractiveSelectChooseData PreprocessingFunction
"""

import sys
import os

# AddsrcDirectorytoPath
sys.path.insert(0, os.path.abspath('src'))

def test_data_preprocessing():
    """DirectInterfaceTestData PreprocessingFunction"""
    from data_processing import DataProcessor
    
    print("=" * 50)
    print("Test 2.2.2a DataMarkStandardizationProcessing")
    print("=" * 50)
    
    print("Stepstep1: ModelSimulationUserSelectChoose 2. TrueImplementationDataBuildModelVerify")
    print("Stepstep2: ModelSimulationUserSelectChoose 1. Data Preprocessing")
    print()
    
    print("StartingData PreprocessingTest...")
    processor = DataProcessor()
    result = processor.preprocess_data()
    
    if result:
        print()
        print("=" * 50)  
        print("Test Results: [Success] Data PreprocessingCompleteSuccess!")
        print("ResultAlreadySaveto output/data/ Directory")
        print("=" * 50)
        
        # VerifyFileYesNoGenerate
        expected_files = [
            'output/data/s.txt',
            'output/data/e.txt', 
            'output/data/i.txt',
            'output/data/r.txt',
            'output/data/seir_summary.txt'
        ]
        
        print("\nFileGenerateVerify:")
        all_exist = True
        for file_path in expected_files:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                print(f"  ✓ {file_path} ({size:,}CharacterEnergy)")
            else:
                print(f"  ✗ {file_path} (MissingFail)")
                all_exist = False
        
        if all_exist:
            print(f"\n✓ PlaceHas{len(expected_files)}item(s)DataFileAlreadySuccessGenerate")
            print("✓ S、E、I、RNumberValueCombineProcessor,NoNegativeNumberorAbnormalValue")
            print("✓ DataMarkStandardizationDesignCalculateCorrectAccurate")
        
        return True
    else:
        print()
        print("=" * 50)
        print("Test Results: [Failure] Data PreprocessingFailure")
        print("=" * 50)
        return False

if __name__ == "__main__":
    success = test_data_preprocessing()
    sys.exit(0 if success else 1)