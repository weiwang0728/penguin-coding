# -*- coding: utf-8 -*-
"""Test ChangeImportIsolationDistanceMachineControlSEIRModelType"""
import sys
import os
sys.path.insert(0, os.path.abspath('src'))
from models.isolation_seir_model import IsolationSEIRModel

print("Test: ChangeImportIsolationDistanceMachineControlSEIRModelType")
model = IsolationSEIRModel()
result = model.run_simulation()
if result:
    print("[Success] IsolationDistanceSEIRModelTypeRunCompleteSuccess!")
else:
    print("[Failure] IsolationDistanceSEIRModelTypeRunFailure")