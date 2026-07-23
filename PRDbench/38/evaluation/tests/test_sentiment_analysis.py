# -*- coding: utf-8 -*-
import pytest
import sys
import os

# AddsrcDirectorytoPythonPath
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from text_mining import TextMining

class TestSentimentAnalysis:
    """SentimentAnalysis-AttributeSentimentRecognitionTest"""
    
    def setup_method(self):
        """TestbeforeStandardPrepare"""
        self.text_mining = TextMining()
    
    def test_sentiment_analysis_attribute_emotion_pairs(self):
        """TestSentimentAnalysisandAttributeSentimentRecognition"""
        # StandardPrepareTestEvaluateReviewData
        positive_review = "thisitem(s)PhonePerformancevery good，outerViewAttractive，PriceFormatImplementationHP"
        negative_review = "QualityEditionNotGood，workmanshipEngineeringRough，PriceFormatTooExpensive"
        
        # ExecuteDivideWordandSentimentAnalysis
        positive_words = self.text_mining.segment_text(positive_review)
        negative_words = self.text_mining.segment_text(negative_review)
        
        positive_score = self.text_mining.calculate_sentiment_score(positive_words)
        negative_score = self.text_mining.calculate_sentiment_score(negative_words)
        
        # Breakassertion：CorrectSurfaceEvaluateReviewSituationInfectionScoreShouldThisasCorrect
        assert positive_score > 0, f"CorrectSurfaceEvaluateReviewSituationInfectionScoreShouldasCorrectNumber，ImplementationInternationalScore：{positive_score}"
        
        # Breakassertion：NegativeSurfaceEvaluateReviewSituationInfectionScoreShouldThisasNegativeorInterfaceNear0
        assert negative_score <= 0, f"NegativeSurfaceEvaluateReviewSituationInfectionScoreShouldasNegativeNumberor0，ImplementationInternationalScore：{negative_score}"
        
        # Breakassertion：UseUseWordClassicOfficialMethodAndNonPretrainedModelType
        assert hasattr(self.text_mining, 'sentiment_dict'), "ShouldThisUseUseSituationInfectionWordClassic"
        assert len(self.text_mining.sentiment_dict) > 0, "SituationInfectionWordClassicNotShouldasEmpty"
        
        # VerifyAttributeSentimentRecognition
        # UseUseImplementationHasanalyze_reviewOfficialMethodComeGetGetAttribute-SituationInfectionfor
        analysis_result = self.text_mining.analyze_review(positive_review)
        attribute_emotion_pairs = analysis_result.get('attribute_scores', {})
        assert len(attribute_emotion_pairs) > 0, "ShouldThisEnergyrecognitionDifferentOutputAttribute-SituationInfectionfor"
        
        return True