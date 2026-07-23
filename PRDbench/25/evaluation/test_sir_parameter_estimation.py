# -*- coding: utf-8 -*-
"""Test SIRModelTypeParameterEstimateDesign"""
import sys; sys.path.append('src')
from parameter_estimation import ParameterEstimator

print("Test: TrueImplementationDataBuildModelVerify → SIRModelTypeParameterEstimateDesign")
estimator = ParameterEstimator()
result = estimator.estimate_sir_parameters()
if result:
    print("[Success] SIRParameterEstimateDesignCompleteSuccess!")
else:
    print("[Failure] SIRParameterEstimateDesignFailure")