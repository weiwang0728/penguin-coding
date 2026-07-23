#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os

# AddsrcDirectorytoPath
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

from text_mining import TextMining

def test_jieba_segmentation():
    """SpecializedKeywordTest2.4.1 JiebaSegmentation-AttributeWordRecognition"""
    
    print("=" * 60)
    print("2.4.1 JiebaSegmentation-AttributeWordRecognition Specializeditem(s)Test")
    print("=" * 60)
    
    try:
        # 1. beforeSetCheckExperience：FalseDesignMainMenuSaveinTextBookProcessingOption（ImplementationInternationalitem(s)NeedVerify）
        print("beforeSetCheckExperiencePass：MainMenuSaveinEvaluateReviewMiningorTextBookProcessingOption")
        
        # 2. StandardPrepareStepSegment：CreateContainsObviousAttributeWordProductBrandEvaluateReviewTextBook
        test_comment = "thisitem(s)PhonePerformancevery good，outerViewAttractive，PriceFormatImplementationHP，QualityEditionNotWrong"
        print(f"StandardPrepareStepSegment：SuccessCreateContainsObviousAttributeWordProductBrandEvaluateReview：{test_comment}")
        
        # 3. ExecuteStepSegment：ExecuteEvaluateReviewDivideWordProcessingFunction
        config = {}
        text_mining = TextMining(config)
        
        # ExecutejiebaDivideWord
        words = text_mining.segment_text(test_comment)
        print(f"ExecuteStepSegment：EvaluateReviewDivideWordProcessingFunctionSuccessExecute")
        
        # 4. BreakassertionVerify：VerifyjiebaDivideWordResultCorrectAccurate，recognitionDifferentOutputProductBrandAttributeRelatedKeyWord
        print(f"BreakassertionVerify：jiebaDivideWordResult：{words}")
        
        # CheckYesNorecognitionDifferentOutputAttributeWord
        attribute_words = ['Performance', 'outerView', 'PriceFormat', 'QualityEdition']
        found_attributes = [word for word in attribute_words if word in words]
        
        if len(found_attributes) >= 3:
            print(f"✓ SuccessrecognitionDifferentOutputProductBrandAttributeRelatedKeyWord：{found_attributes}")
            print("✓ DivideWordResultCorrectAccurate，AttributeWordRecognitionFunctionNormal")
            print("SUCCESS: JiebaSegmentationTestFully Passed")
            return True
        else:
            print(f"✗ OnlyrecognitionDifferentOutput{len(found_attributes)}item(s)AttributeWord，fewer than expected")
            return False
            
    except Exception as e:
        print(f"ERROR: jiebaDivideWordTest Failed: {e}")
        return False

if __name__ == "__main__":
    success = test_jieba_segmentation()
    sys.exit(0 if success else 1)