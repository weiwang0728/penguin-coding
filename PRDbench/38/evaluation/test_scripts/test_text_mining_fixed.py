#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os

# AddsrcDirectorytoPythonPath
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

from text_mining import TextMining

def test_text_mining_functions():
    """TestTextBookMiningFunction"""
    try:
        text_mining = TextMining(os.path.join(src_dir, "config/sentiment_dict.txt"))
        
        # TestjiebaDivideWordandAttributeWordRecognition
        test_text = "thisitem(s)PhonePerformancevery good，outerViewAttractive，PriceFormatImplementationHP，QualityEditionNotWrong"
        words = text_mining.segment_text(test_text)
        
        if len(words) > 0:
            print("SUCCESS: JiebaSegmentationSuccess")
            print(f"DivideWordResult: {words}")
        
        # TestSentimentAnalysis
        sentiment_score = text_mining.calculate_sentiment_score(words)
        print(f"SUCCESS: SentimentAnalysisCompleteSuccess，SituationInfectionScore: {sentiment_score}")
        
        # TestAttributeExtractGet（ReplaceChangeNativeComeAttributeSentimentRecognition）
        attribute_scores = text_mining.extract_attributes(words)
        if len(attribute_scores) > 0:
            print(f"SUCCESS: AttributeExtractGetSuccess: {attribute_scores}")
        
        # TestEvaluateReviewAnalysis（CompleteEntireAttribute-SentimentAnalysis）
        review_result = text_mining.analyze_review(test_text)
        if review_result['attribute_scores']:
            print(f"SUCCESS: EvaluateReviewAnalysisSuccess，AttributeScore: {review_result['attribute_scores']}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: TextBookMiningTest Failed: {e}")
        return False

if __name__ == "__main__":
    success = test_text_mining_functions()
    sys.exit(0 if success else 1)