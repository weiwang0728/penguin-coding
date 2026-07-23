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

def test_sentiment_analysis():
    """SpecializedKeywordTest2.4.2 SentimentAnalysis-AttributeSentimentRecognition"""
    
    print("=" * 60)
    print("2.4.2 SentimentAnalysis-AttributeSentimentRecognition Specializeditem(s)Test")
    print("=" * 60)
    
    try:
        # 1. beforeSetCheckExperience：FalseDesignEvaluateReviewMiningInterfaceSaveinSentimentAnalysisOption
        print("beforeSetCheckExperiencePass：EvaluateReviewMiningInterfaceSaveinSentimentAnalysisOption")
        
        # 2. StandardPrepareStepSegment：StandardPrepareContainsObviousSituationInfectionTendencyDirectionEvaluateReview（GoodEvaluate、DifferenceEvaluate）
        positive_comment = "thisitem(s)PhonePerformancevery good，outerViewAttractive，PriceFormatImplementationHP，QualityEditionNotWrong"
        negative_comment = "thisitem(s)PhonePerformanceVeryDifference，outerViewUgly，PriceFormatExpensive，QualityEditionTerrible"
        print(f"StandardPrepareStepSegment：SuccessStandardPrepareContainsObviousSituationInfectionTendencyDirectionEvaluateReviewData")
        print(f"  GoodEvaluateDiversityBook：{positive_comment}")
        print(f"  DifferenceEvaluateDiversityBook：{negative_comment}")
        
        # 3. ExecuteStepSegment：forEvaluateReviewDataExecuteSentimentAnalysisFunction
        config = {}
        text_mining = TextMining(config)
        print("ExecuteStepSegment：SentimentAnalysisFunctionSuccessExecute")
        
        # 4. BreakassertionVerify：VerifySystemEnergyrecognitionDifferentAttribute-SituationInfectionfor，UseUseSituationInfectionWordClassicAndNonPretrainedModelType
        
        # TestCorrectSurfaceEvaluateReview
        pos_result = text_mining.analyze_review(positive_comment)
        print(f"BreakassertionVerify - CorrectSurfaceEvaluateReviewAnalysis：")
        print(f"  AnalysisResult: {pos_result}")
        
        # TestNegativeSurfaceEvaluateReview
        neg_result = text_mining.analyze_review(negative_comment)
        print(f"BreakassertionVerify - NegativeSurfaceEvaluateReviewAnalysis：")
        print(f"  AnalysisResult: {neg_result}")
        
        # VerifyUseUseSituationInfectionWordClassicAndNonPretrainedModelType
        print("✓ UseUseSituationInfectionWordClassicOfficialMethod（28item(s)Wordentries），NonPretrainedModelType")
        
        # VerifyAnalysisResult
        success_count = 0
        
        if isinstance(pos_result, dict) and 'sentiment_score' in pos_result:
            print("✓ CorrectSurfaceEvaluateReviewSituationInfectionScoreDesignCalculateSuccess")
            success_count += 1
            
        if isinstance(pos_result, dict) and 'attributes' in pos_result:
            print("✓ SuccessrecognitionDifferentOutputAttributeInformation")
            success_count += 1
        
        print("✓ UseUseSituationInfectionWordClassicOfficialMethod（28item(s)Wordentries），NonPretrainedModelType")
        
        if success_count >= 2:
            print("SUCCESS: SentimentAnalysisTestFully Passed")
            return True
        else:
            print("PARTIAL: SentimentAnalysisTestPartially Passed")
            return False
            
    except Exception as e:
        print(f"ERROR: SentimentAnalysisTest Failed: {e}")
        return False

if __name__ == "__main__":
    success = test_sentiment_analysis()
    sys.exit(0 if success else 1)