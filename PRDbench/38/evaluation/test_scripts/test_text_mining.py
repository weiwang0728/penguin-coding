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
        
        # TestAttributeSentimentRecognition
        emotion_pairs = text_mining.extract_attribute_emotion_pairs(test_text)
        if len(emotion_pairs) > 0:
            print(f"SUCCESS: AttributeSentimentRecognitionSuccess: {emotion_pairs}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: TextBookMiningTest Failed: {e}")
        return False

if __name__ == "__main__":
    success = test_text_mining_functions()
    sys.exit(0 if success else 1)
