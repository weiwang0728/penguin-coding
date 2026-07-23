# -*- coding: utf-8 -*-
import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from text_mining import TextMining

def test_comment_weight_fusion():
    """TestReviewWeightFusionandPreferenceDirectionEditionUpdate"""
    text_mining = TextMining()
    
    # TestEvaluateReviewData
    user_comments = ["Performancevery good，outerViewAttractive", "PriceFormatImplementationHP，QualityEditionNotWrong"]
    
    # ExecuteWeightWeightFusionCombine
    # ModelSimulationEvaluateReviewDataFrame
    import pandas as pd
    reviews_df = pd.DataFrame({
        'user_id': [1, 1],
        'review_text': user_comments,
        'product_id': [1, 2]
    })
    
    # ExecuteWeightWeightFusionCombine
    preference_update = text_mining.build_user_preference_from_reviews(1, reviews_df)
    
    # Breakassertion：WeightWeightUpdateCombineProcessor
    assert preference_update is not None, "ShouldThisEnergyUpdateUserPreference"
