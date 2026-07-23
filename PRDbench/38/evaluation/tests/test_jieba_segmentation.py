# -*- coding: utf-8 -*-
import pytest
import sys
import os

# AddsrcDirectorytoPythonPath
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from text_mining import TextMining

class TestJiebaSegmentation:
    """JiebaSegmentation-AttributeWordRecognitionTest"""
    
    def setup_method(self):
        """TestbeforeStandardPrepare"""
        self.text_mining = TextMining()
    
    def test_jieba_segmentation_attribute_recognition(self):
        """TestjiebaDivideWordandAttributeWordRecognition"""
        # TestTextBookContainsObviousAttributeWord
        test_text = "thisitem(s)PhonePerformancevery good，outerViewAttractive，PriceFormatImplementationHP，QualityEditionNotWrong，FunctionStrongLarge"
        
        # ExecuteDivideWord
        words = self.text_mining.segment_text(test_text)
        
        # Breakassertion：DivideWordResultNotasEmpty
        assert len(words) > 0, "DivideWordResultNotShouldasEmpty"
        
        # Breakassertion：EnergyrecognitionDifferentOutputAttributeCameraRelatedWordentries
        attribute_words_found = []
        for category, keywords in self.text_mining.attribute_keywords.items():
            for keyword in keywords:
                if keyword in words or any(keyword in word for word in words):
                    attribute_words_found.append(keyword)
        
        # Breakassertion：RecognizeAtLeastDifferentOutput3item(s)AttributeWord
        assert len(attribute_words_found) >= 3, f"ShouldrecognitionDifferentOutputToFew3item(s)AttributeWord，ImplementationInternationalrecognitionDifferent：{attribute_words_found}"
        
        # Breakassertion：DivideWordUseUsejieba（VerifyDivideWordQualityEdition）
        assert 'Performance' in words, "ShouldThisCorrectAccuraterecognitionDifferent'Performance'AttributeWord"
        assert 'outerView' in words or 'attractive' in words, "ShouldThisCorrectAccuraterecognitionDifferentouterViewCameraRelatedAttributeWord"
        assert 'PriceFormat' in words or 'ImplementationHP' in words, "ShouldThisCorrectAccuraterecognitionDifferentPriceFormatCameraRelatedAttributeWord"
        
        return True