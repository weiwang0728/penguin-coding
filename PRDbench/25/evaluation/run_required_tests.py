# -*- coding: utf-8 -*-
"""
onlyRundetailedTestDesignplaninRequirementsTest Case
"""

import subprocess
import sys

# detailedTestDesignplanin18item(s)ToolIntegratedpytestTest Command
REQUIRED_TESTS = [
    "python -m pytest evaluation/tests/test_si_model_algorithm.py::TestSIModelAlgorithm::test_si_model_core_algorithm -v",
    "python -m pytest evaluation/tests/test_sir_model_algorithm.py::TestSIRModelAlgorithm::test_sir_model_core_algorithm -v", 
    "python -m pytest evaluation/tests/test_sir_model_algorithm.py::TestSIRModelAlgorithm::test_sir_model_parameter_validation -v",
    "python -m pytest evaluation/tests/test_seir_model_algorithm.py::TestSEIRModelAlgorithm::test_seir_model_core_algorithm -v",
    "python -m pytest evaluation/tests/test_data_field_extraction.py::TestDataFieldExtraction::test_key_field_extraction_and_validation -v",
    "python -m pytest evaluation/tests/test_data_field_extraction.py::TestDataFieldExtraction::test_field_extraction_with_real_data -v",
    "python -m pytest evaluation/tests/test_isolation_effectiveness.py::TestIsolationEffectiveness::test_isolation_reduces_infection_peak -v",
    "python -m pytest evaluation/tests/test_brownian_motion.py::TestBrownianMotion::test_brownian_motion_characteristics -v",
    "python -m pytest evaluation/tests/test_spatial_distance_calculation.py::TestSpatialDistanceCalculation::test_spatial_distance_calculation_accuracy -v",
    "python -m pytest evaluation/tests/test_spatial_transmission_probability.py::TestSpatialTransmissionProbability::test_transmission_probability_distance_correlation -v",
    "python -m pytest evaluation/tests/test_spatial_isolation_management.py::TestSpatialIsolationManagement::test_isolation_prevents_movement -v",
    "python -m pytest evaluation/tests/test_exception_handling.py::TestExceptionHandling::test_invalid_file_path_handling -v",
    "python -m pytest evaluation/tests/test_runtime_performance.py::TestRuntimePerformance::test_complete_simulation_runtime -v",
    "python -m pytest evaluation/tests/test_memory_performance.py::TestMemoryPerformance::test_peak_memory_usage_constraint -v",
    "python -m pytest evaluation/tests/test_code_modularity.py::TestCodeModularity::test_module_structure_clarity -v",
    "python -m pytest evaluation/tests/test_code_standards.py::TestCodeStandards::test_code_comment_coverage -v",
    "python -m pytest evaluation/tests/test_unit_test_coverage.py::TestUnitTestCoverage::test_unit_test_files_existence -v"
]

def run_required_tests():
    """RundetailedTestDesignplaninRequirementsTest"""
    print("=" * 80)
    print("RundetailedTestDesignplaninRequirementsUnit Test")
    print("=" * 80)
    
    passed = 0
    failed = 0
    failed_tests = []
    
    for i, test_command in enumerate(REQUIRED_TESTS, 1):
        print(f"\n[{i}/{len(REQUIRED_TESTS)}] RunTest...")
        print(f"Command: {test_command}")
        
        try:
            result = subprocess.run(test_command, shell=True, capture_output=True, text=True,
                                  cwd='.', timeout=60)
            
            if result.returncode == 0:
                print("[PASSED] Test Passed")
                passed += 1
            else:
                print(f"[FAILED] Test Failed")
                failed += 1
                failed_tests.append(test_command.split('::')[-1].split(' ')[0])
                print(f"ErrorInformation: {result.stderr[:200]}...")
        except subprocess.TimeoutExpired:
            print("[TIMEOUT] TestUltraTime")
            failed += 1
            failed_tests.append("TIMEOUT")
        except Exception as e:
            print(f"[ERROR] ExecuteAbnormal: {str(e)}")
            failed += 1
            failed_tests.append("ERROR")
    
    # summarySummaryResult
    print("\n" + "=" * 80)
    print("detailedTestDesignplanRequirementsSingleunitTest ResultssummaryTotal")
    print("=" * 80)
    
    total = len(REQUIRED_TESTS)
    success_rate = (passed / total) * 100
    
    print(f"TotalTestNumber: {total}")
    print(f"Pass: {passed}")
    print(f"Failure: {failed}")
    print(f"SuccessRate: {success_rate:.1f}%")
    
    if failed_tests:
        print(f"\nFailureTest:")
        for test in failed_tests:
            print(f"  - {test}")
    
    # CheckYesNoSymbolCombine3.3bRequirements100%Pass Rate
    if success_rate == 100.0:
        print(f"\n[SUCCESS] SymbolCombine3.3bRequirements: Test PassedRate100%,NoTest FailedUseExample")
        return True
    else:
        print(f"\n[FAIL] NotSymbolCombine3.3bRequirements: Test PassedRate{success_rate:.1f}% < 100%")
        return False

if __name__ == "__main__":
    success = run_required_tests()
    sys.exit(0 if success else 1)