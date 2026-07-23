# -*- coding: utf-8 -*-
"""
RunTimeBetweenPerformanceTestUnit Test
TestSystemEachModuleRunTimeBetweenPerformance
"""

import pytest
import time
import numpy as np
import os
import sys
import psutil
import threading
from contextlib import contextmanager

# AddsrcDirectorytoPath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from data_processing import DataProcessor
from models.sir_model import SIRModel
from models.seir_model import SEIRModel
from models.isolation_seir_model import IsolationSEIRModel
from models.spatial_brownian_model import SpatialBrownianModel
from utils import create_directories


@contextmanager
def performance_timer():
    """PerformanceDesignTimeDeviceonunderTextManagementDevice"""
    start_time = time.time()
    yield lambda: time.time() - start_time
    end_time = time.time()


class TestRuntimePerformance:
    """RunTimeBetweenPerformanceTestCategory"""
    
    def setup_method(self):
        """eachitem(s)TestOfficialMethodbeforeDesignSet"""
        self.max_acceptable_time = 30  # MostLargeCanInterfaceacceptableRunTimeBetween(Second)
        self.long_simulation_days = 200  # LengthTimeBetweenSequenceSeriesModelSimulationDayNumber
        
    def test_complete_simulation_runtime(self):
        """TestCompleteEntireModelSimulationRunTimeBetween
        
        Verify:
        1. SingleTimesCompleteEntireModelSimulationRunTimeBetween≤30Second
        2. SupportSupport≥200DayLengthTimeBetweenSequenceSeriesModelSimulation
        """
        
        print("StartingCompleteEntireModelSimulationPerformanceTest...")
        
        # AccurateProtectionOutputDirectorySavein
        create_directories()
        
        with performance_timer() as get_elapsed:
            # 1. Data ProcessingPerformanceTest
            print("TestData ProcessingPerformance...")
            data_start = time.time()
            
            processor = DataProcessor()
            processor.create_sample_data()
            processor.validate_data()
            processor.calculate_seir_states()
            processor.save_processed_data()
            
            data_time = time.time() - data_start
            print(f"Data ProcessingUseTime: {data_time:.2f}Second")
            
            # 2. SIRModelTypePerformanceTest
            print("TestSIRModelTypePerformance...")
            sir_start = time.time()
            
            sir_config = {
                'N': 10000,
                'beta': 0.05,
                'gamma': 0.1,
                'S0': 9999,
                'I0': 1,
                'R0': 0,
                'days': self.long_simulation_days,  # 200DayLengthTimeBetweenSequenceSeries
                'dt': 1
            }
            
            sir_model = SIRModel(sir_config)
            sir_model.solve_ode()
            sir_model.plot_results()
            
            sir_time = time.time() - sir_start
            print(f"SIRModelTypeUseTime: {sir_time:.2f}Second")
            
            # 3. SEIRModelTypePerformanceTest
            print("TestSEIRModelTypePerformance...")
            seir_start = time.time()
            
            seir_config = {
                'N': 10000,
                'beta': 0.03,
                'sigma': 0.1,
                'gamma': 0.1,
                'r': 20,                 # AddInterfaceTouchRateParameter
                'S0': 9999,
                'E0': 0,
                'I0': 1,
                'R0': 0,
                'days': self.long_simulation_days,  # 200DayLengthTimeBetweenSequenceSeries
                'dt': 1
            }
            
            seir_model = SEIRModel(seir_config)
            seir_model.solve_ode()
            seir_model.plot_results()
            
            seir_time = time.time() - seir_start
            print(f"SEIRModelTypeUseTime: {seir_time:.2f}Second")
            
            # 4. IsolationDistanceSEIRModelTypePerformanceTest(CameraforRecoverymisc)
            print("TestIsolationDistanceSEIRModelTypePerformance...")
            isolation_start = time.time()
            
            isolation_config = {
                'N': 10000,
                'beta': 0.03,
                'sigma': 0.1,
                'gamma': 0.1,
                'q': 0.01,
                'deltaI': 0.13,
                'gammaI': 0.007,
                'lambda_val': 0.03,
                'deltaH': 0.008,
                'alpha': 0.0001,
                'S0': 9999,
                'E0': 0,
                'I0': 1,
                'Sq0': 0,
                'Eq0': 0,
                'H0': 0,
                'R0': 0,
                'days': 100,  # SuitableinDayNumber
                'dt': 1
            }
            
            isolation_model = IsolationSEIRModel(isolation_config)
            isolation_model.solve_ode()
            isolation_model.plot_results()
            
            isolation_time = time.time() - isolation_start
            print(f"IsolationDistanceSEIRModelTypeUseTime: {isolation_time:.2f}Second")
        
        # DesignCalculateTotalRunTimeBetween
        total_time = get_elapsed()
        
        print(f"\nPerformanceTest Results:")
        print(f"Data Processing: {data_time:.2f}Second")
        print(f"SIRModelType({self.long_simulation_days}Day): {sir_time:.2f}Second")
        print(f"SEIRModelType({self.long_simulation_days}Day): {seir_time:.2f}Second")
        print(f"IsolationDistanceSEIRModelType(100Day): {isolation_time:.2f}Second")
        print(f"TotalRunTimeBetween: {total_time:.2f}Second")
        
        # VerifyPerformance Requirements
        assert total_time <= self.max_acceptable_time, \
            f"CompleteEntireModelSimulationRunTimeBetween{total_time:.2f}SecondUltraOverLimitedControl{self.max_acceptable_time}Second"
        
        # VerifySupportSupportLengthTimeBetweenSequenceSeriesModelSimulation
        assert sir_config['days'] >= 200, f"ShouldSupportSupport≥200DayModelSimulation,ImplementationInternationalSupportSupport{sir_config['days']}Day"
        assert seir_config['days'] >= 200, f"ShouldSupportSupport≥200DayModelSimulation,ImplementationInternationalSupportSupport{seir_config['days']}Day"
        
        print("CompleteEntireModelSimulationRunTimeBetweenPerformanceTest Passed")
    
    def test_individual_component_performance(self):
        """TestEachitem(s)GroupPieceSingleindependentPerformance"""
        
        # TestData ProcessingGroupPiecePerformance
        with performance_timer() as get_elapsed:
            processor = DataProcessor()
            processor.create_sample_data()
        
        data_creation_time = get_elapsed()
        assert data_creation_time <= 5.0, \
            f"DataCreateUseTime{data_creation_time:.2f}SecondUltraOver5SecondLimitedControl"
        
        # TestDataVerifyPerformance
        with performance_timer() as get_elapsed:
            processor.validate_data()
        
        validation_time = get_elapsed()
        assert validation_time <= 2.0, \
            f"DataVerifyUseTime{validation_time:.2f}SecondUltraOver2SecondLimitedControl"
        
        # TestSEIRStatusDesignCalculatePerformance
        with performance_timer() as get_elapsed:
            processor.calculate_seir_states()
        
        calculation_time = get_elapsed()
        assert calculation_time <= 3.0, \
            f"SEIRDesignCalculateUseTime{calculation_time:.2f}SecondUltraOver3SecondLimitedControl"
        
        print(f"GroupPiecePerformanceTest:")
        print(f"DataCreate: {data_creation_time:.2f}Second")
        print(f"DataVerify: {validation_time:.2f}Second")
        print(f"SEIRDesignCalculate: {calculation_time:.2f}Second")
        
        print("GroupPiecePerformanceTest Passed")
    
    def test_scalability_performance(self):
        """TestSystemExtendextensionPerformance(NotSameRuleModelData)"""
        
        population_sizes = [1000, 5000, 10000, 20000]
        performance_results = []
        
        for N in population_sizes:
            config = {
                'N': N,
                'beta': 0.05,
                'gamma': 0.1,
                'S0': N-1,
                'I0': 1,
                'R0': 0,
                'days': 50,  # fixedFixedDayNumbertoBiferCompareExtendextensionness
                'dt': 1
            }
            
            with performance_timer() as get_elapsed:
                model = SIRModel(config)
                model.solve_ode()
            
            runtime = get_elapsed()
            performance_results.append((N, runtime))
            print(f"PersonPort{N}: {runtime:.2f}Second")
        
        # VerifyExtendextensionnessCombineProcessor(TimeBetweenRecoverymiscDegreesNotShouldOverHigh)
        # PersonPortIncreasePlus20times,TimeBetweenNotShouldIncreasePlusUltraOver100times
        time_ratio = performance_results[-1][1] / performance_results[0][1]
        population_ratio = population_sizes[-1] / population_sizes[0]
        
        efficiency_ratio = time_ratio / population_ratio
        
        print(f"ExtendextensionnessAnalysis:")
        print(f"PersonPortExtendmultiplesNumber: {population_ratio}")
        print(f"TimeBetweenIncreaseLengthtimesNumber: {time_ratio:.2f}")
        print(f"EffectRateBifer: {efficiency_ratio:.2f}")
        
        assert efficiency_ratio <= 5.0, \
            f"ExtendextensionnessEffectRateBifer{efficiency_ratio:.2f}OverHigh,SystemExtendextensionnessNotgood"
        
        print("ExtendextensionPerformanceTest Passed")
    
    def test_long_duration_simulation_performance(self):
        """TestLengthTimeBetweenModelSimulationPerformancestableFixedness"""
        
        # TestNotSameDayNumberModelSimulationPerformance
        day_configs = [50, 100, 200, 365]  # ContainsOneyearModelSimulation
        
        for days in day_configs:
            config = {
                'N': 10000,
                'beta': 0.03,
                'sigma': 0.1,
                'gamma': 0.1,
                'S0': 9999,
                'E0': 0,
                'I0': 1,
                'R0': 0,
                'days': days,
                'dt': 1
            }
            
            with performance_timer() as get_elapsed:
                model = SEIRModel(config)
                model.solve_ode()
            
            runtime = get_elapsed()
            time_per_day = runtime / days
            
            print(f"{days}DayModelSimulation: {runtime:.2f}Second (eachDay{time_per_day:.4f}Second)")
            
            # VerifyTimeBetweenRecoverymiscDegreesFoundationBookLineness
            assert time_per_day <= 0.1, \
                f"{days}DayModelSimulationeachDayUseTime{time_per_day:.4f}SecondOverLength"
            
            # VerifyLengthTimeBetweenModelSimulationstillinCanInterfaceacceptableRangerangeInternal
            if days >= 200:
                assert runtime <= self.max_acceptable_time, \
                    f"{days}DayModelSimulationUseTime{runtime:.2f}SecondUltraOver{self.max_acceptable_time}SecondLimitedControl"
        
        print("LengthTimeBetweenModelSimulationPerformanceTest Passed")
    
    def test_concurrent_performance(self):
        """TestparallelSendPerformance(Manyitem(s)ModelTypeSameTimeRun)"""
        
        def run_sir_model(model_id):
            """RunSIRModelTypeFunctionNumber"""
            config = {
                'N': 5000,
                'beta': 0.05,
                'gamma': 0.1,
                'S0': 4999,
                'I0': 1,
                'R0': 0,
                'days': 100,
                'dt': 1
            }
            
            model = SIRModel(config)
            start_time = time.time()
            model.solve_ode()
            end_time = time.time()
            
            return model_id, end_time - start_time
        
        # TestForwardSequenceExecute
        sequential_start = time.time()
        sequential_results = []
        for i in range(3):
            model_id, runtime = run_sir_model(i)
            sequential_results.append(runtime)
        sequential_total = time.time() - sequential_start
        
        # TestparallelSendExecute
        concurrent_start = time.time()
        threads = []
        concurrent_results = []
        
        def thread_wrapper(model_id):
            result = run_sir_model(model_id)
            concurrent_results.append(result[1])
        
        for i in range(3):
            thread = threading.Thread(target=thread_wrapper, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        concurrent_total = time.time() - concurrent_start
        
        print(f"PerformanceforBifer:")
        print(f"ForwardSequenceExecute: {sequential_total:.2f}Second")
        print(f"parallelSendExecute: {concurrent_total:.2f}Second")
        print(f"PlusSpeedBifer: {sequential_total/concurrent_total:.2f}x")
        
        # VerifyparallelSendExecuteHasPerformanceExtractrise(at_leastless_thanEnergyProvince20%TimeBetween)
        speedup = sequential_total / concurrent_total
        assert speedup >= 1.2, f"parallelSendExecutePlusSpeedBifer{speedup:.2f}LowAt1.2"
        
        print("parallelSendPerformanceTest Passed")
    
    def test_performance_consistency(self):
        """TestPerformanceOneCauseness(ManyTimesRunResultstableFixed)"""
        
        config = {
            'N': 10000,
            'beta': 0.05,
            'gamma': 0.1,
            'S0': 9999,
            'I0': 1,
            'R0': 0,
            'days': 100,
            'dt': 1
        }
        
        # ManyTimesRunCameraSameConfigure
        runtimes = []
        num_runs = 5
        
        for run in range(num_runs):
            with performance_timer() as get_elapsed:
                model = SIRModel(config)
                model.solve_ode()
            
            runtime = get_elapsed()
            runtimes.append(runtime)
            print(f"index{run+1}TimesRun: {runtime:.2f}Second")
        
        # DesignCalculatePerformanceSystemDesign
        mean_time = np.mean(runtimes)
        std_time = np.std(runtimes)
        cv = std_time / mean_time  # ChangeDifferentSeriesNumber
        
        print(f"PerformanceSystemDesign:")
        print(f"AverageAverageTimeBetween: {mean_time:.2f}Second")
        print(f"MarkStandardDifference: {std_time:.2f}Second")
        print(f"ChangeDifferentSeriesNumber: {cv:.2f}")
        
        # VerifyPerformanceOneCauseness(ChangeDifferentSeriesNumberShouldSmallAt20%)
        assert cv <= 0.2, f"PerformanceChangeDifferentSeriesNumber{cv:.2f}OverHigh,PerformanceNotstableFixed"
        
        # VerifyPlaceHasRunallinCanInterfaceacceptableTimeBetweenInternal
        for i, runtime in enumerate(runtimes):
            assert runtime <= self.max_acceptable_time, \
                f"index{i+1}TimesRunUseTime{runtime:.2f}SecondUltraOverLimitedControl"
        
        print("PerformanceOneCausenessTest Passed")


if __name__ == "__main__":
    # RunTest
    test_instance = TestRuntimePerformance()
    test_instance.setup_method()
    
    try:
        test_instance.test_complete_simulation_runtime()
        test_instance.test_individual_component_performance()
        test_instance.test_scalability_performance()
        test_instance.test_long_duration_simulation_performance()
        test_instance.test_concurrent_performance()
        test_instance.test_performance_consistency()
        print("\nPlaceHasRunTimeBetweenPerformanceTest Passed!")
    except AssertionError as e:
        print(f"\nTest Failed: {e}")
    except Exception as e:
        print(f"\nTestOutputWrong: {e}")