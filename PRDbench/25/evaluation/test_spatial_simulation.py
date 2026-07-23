# -*- coding: utf-8 -*-
"""Test EmptyBetweenTraditionalSpreadModelSimulation"""
import sys; sys.path.append('src')
from models.spatial_brownian_model import SpatialBrownianModel

print("Test: DistributionrandomSportsEmptyBetweenTraditionalSpreadOptimizeization → EmptyBetweenTraditionalSpreadModelSimulation") 
model = SpatialBrownianModel()
result = model.run_simulation()
if result:
    print("[Success] EmptyBetweenTraditionalSpreadModelSimulationCompleteSuccess!")
else:
    print("[Failure] EmptyBetweenTraditionalSpreadModelSimulationFailure")