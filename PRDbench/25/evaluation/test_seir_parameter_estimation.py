# -*- coding: utf-8 -*-
"""Test SEIRModelTypeParameterEstimateDesign"""
import sys; sys.path.append('src')  
from parameter_estimation import ParameterEstimator

print("Test: TrueImplementationDataBuildModelVerify → SEIRModelTypeParameterEstimateDesign")
estimator = ParameterEstimator()
result = estimator.estimate_seir_parameters()
if result:
    print("[Success] SEIRParameterEstimateDesignCompleteSuccess!")
else:
    print("[Failure] SEIRParameterEstimateDesignFailure")