# -*- coding: utf-8 -*-
"""Test RunCompleteEntireEmptyBetweenTraditionalSpreadAnalysis"""
import sys; sys.path.append('src')
from models.spatial_brownian_model import SpatialBrownianModel

print("Test: DistributionrandomSportsEmptyBetweenTraditionalSpreadOptimizeization → RunCompleteEntireEmptyBetweenTraditionalSpreadAnalysis")
model = SpatialBrownianModel()
model.run_simulation()
model.generate_animation_frames()
print("[Success] CompleteEntireEmptyBetweenTraditionalSpreadAnalysisCompleteSuccess!")