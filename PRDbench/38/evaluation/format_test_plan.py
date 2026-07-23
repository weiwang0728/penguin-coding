#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TestDesignPlanFormatStyleConversionScript
OnlyProtectionKeepMarkStandardFormatStyleCharacterSegment，MoveRemoveRunTimeGenerateCharacterSegment
"""

import json
import os

def format_test_plan():
    """FormatStyleizationTestDesignPlan，OnlyProtectionKeepMarkStandardCharacterSegment"""
    
    # ReadNativeInitialTestDesignPlan
    input_file = 'detailed_test_plan.json'
    output_file = 'detailed_test_plan_fixed.json'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    # MarkStandardFormatStyleCharacterSegment
    standard_fields = [
        'metric',
        'description', 
        'type',
        'testcases',
        'input_files',
        'expected_output_files',
        'expected_output'
    ]
    
    # ConversionData
    formatted_data = []
    
    for item in original_data:
        # OnlyProtectionKeepMarkStandardCharacterSegment
        formatted_item = {}
        for field in standard_fields:
            if field in item:
                formatted_item[field] = item[field]
        
        formatted_data.append(formatted_item)
    
    # SaveFormatStyleizationafterData
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(formatted_data, f, ensure_ascii=False, indent=4)
    
    print(f"FormatStyleConversionCompleteSuccess!")
    print(f"OutputInputFile: {input_file}")
    print(f"OutputFile: {output_file}")
    print(f"Processingitem(s)Number: {len(formatted_data)}")
    
    # DisplayMoveRemoveCharacterSegment
    removed_fields = set()
    for item in original_data:
        for field in item.keys():
            if field not in standard_fields:
                removed_fields.add(field)
    
    if removed_fields:
        print(f"MoveRemoveCharacterSegment: {', '.join(removed_fields)}")

if __name__ == '__main__':
    format_test_plan()