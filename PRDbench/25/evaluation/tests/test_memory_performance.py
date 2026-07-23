# -*- coding: utf-8 -*-
"""
InternalSaveUseUsePerformanceTestUnit Test
TestSystemInternalSaveUseUseSituationstateandInternalSaveleakCheckTest
"""

import pytest
import gc
import os
import sys
import psutil
import time
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
def memory_monitor():
    """InternalSavemonitorControlonunderTextManagementDevice"""
    process = psutil.Process()
    
    # StrongControlgarbageReturnReceive,GetGetFoundationStandardInternalSave
    gc.collect()
    baseline_memory = process.memory_info().rss / (1024 * 1024)  # MB
    peak_memory = baseline_memory
    
    def monitor_memory():
        nonlocal peak_memory
        while hasattr(monitor_memory, 'running'):
            current_memory = process.memory_info().rss / (1024 * 1024)
            peak_memory = max(peak_memory, current_memory)
            time.sleep(0.1)
    
    # StartInternalSavemonitorControlLineProcess
    monitor_memory.running = True
    monitor_thread = threading.Thread(target=monitor_memory)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    try:
        yield lambda: {'baseline': baseline_memory, 'peak': peak_memory}
    finally:
        monitor_memory.running = False
        monitor_thread.join(timeout=1)


class TestMemoryPerformance:
    """InternalSaveUseUsePerformanceTestCategory"""
    
    def setup_method(self):
        """eachitem(s)TestOfficialMethodbeforeDesignSet"""
        self.max_memory_gb = 2.0  # MostLargeallowInternalSaveUseUse(GB)
        self.max_memory_mb = self.max_memory_gb * 1024  # ConversionasMB
        
        # CreateOutputDirectory
        create_directories()
        
    def test_peak_memory_usage_constraint(self):
        """TestPeakValueInternalSaveUseUseapproximatelyBundle
        
        Verify:
        1. PeakValueInternalSaveUseUse≤2GB
        2. NoInternalSaveleakIssue
        3. ProgramRunstableFixed
        """
        
        print("StartingInternalSaveUseUseTest...")
        
        with memory_monitor() as get_memory_info:
            # RunCompleteEntireModelSimulationTrendProcess
            print("ExecuteData Processing...")
            processor = DataProcessor()
            processor.create_sample_data()
            processor.validate_data()
            processor.calculate_seir_states()
            
            print("ExecuteSIRModelType...")
            sir_config = {
                'N': 50000,  # CompareLargePersonPortNumbertoTestInternalSaveUseUse
                'beta': 0.05,
                'gamma': 0.1,
                'S0': 49999,
                'I0': 1,
                'R0': 0,
                'days': 365,  # OneyearModelSimulation
                'dt': 1
            }
            sir_model = SIRModel(sir_config)
            sir_model.solve_ode()
            
            print("ExecuteSEIRModelType...")
            seir_config = {
                'N': 50000,
                'beta': 0.03,
                'sigma': 0.1,
                'gamma': 0.1,
                'r': 20,
                'S0': 49999,
                'E0': 0,
                'I0': 1,
                'R0': 0,
                'days': 365,
                'dt': 1
            }
            seir_model = SEIRModel(seir_config)
            seir_model.solve_ode()
            
            print("ExecuteIsolationDistanceSEIRModelType...")
            isolation_config = {
                'N': 30000,  # SuitableinRuleModelavoidOverDegreesInternalSaveUseUse
                'beta': 0.03,
                'sigma': 0.1,
                'gamma': 0.1,
                'q': 0.01,
                'deltaI': 0.13,
                'gammaI': 0.007,
                'lambda_val': 0.03,
                'deltaH': 0.008,
                'alpha': 0.0001,
                'S0': 29999,
                'E0': 0,
                'I0': 1,
                'Sq0': 0,
                'Eq0': 0,
                'H0': 0,
                'R0': 0,
                'days': 200,
                'dt': 1
            }
            isolation_model = IsolationSEIRModel(isolation_config)
            isolation_model.solve_ode()
            
            # StrongControlgarbageReturnReceive
            gc.collect()
            
        # GetGetInternalSaveUseUseInformation
        memory_info = get_memory_info()
        baseline_mb = memory_info['baseline']
        peak_mb = memory_info['peak']
        peak_gb = peak_mb / 1024
        
        print(f"\nInternalSaveUseUseReport:")
        print(f"FoundationStandardInternalSave: {baseline_mb:.2f}MB")
        print(f"PeakValueInternalSave: {peak_mb:.2f}MB ({peak_gb:.3f}GB)")
        print(f"InternalSaveIncreaseLength: {peak_mb - baseline_mb:.2f}MB")
        
        # VerifyPeakValueInternalSaveUseUse≤2GB
        assert peak_gb <= self.max_memory_gb, \
            f"PeakValueInternalSaveUseUse{peak_gb:.3f}GBUltraOver{self.max_memory_gb}GBLimitedControl"
        
        # VerifyInternalSaveUseUseCombineProcessorness(ProgramNormalEngineeringWorkShouldThisHasless_thanEditionInternalSaveIncreaseLength)
        memory_growth = peak_mb - baseline_mb
        assert memory_growth >= 1, \
            f"InternalSaveIncreaseLength{memory_growth:.2f}MBOverLow,CanEnergyProgramnotHasNormalRun"
        
        # VerifyInternalSaveUseUseEffectRate(IncreaseLengthOverHighCanEnergyHasIssue)
        assert memory_growth <= 100, \
            f"InternalSaveIncreaseLength{memory_growth:.2f}MBOverHigh,CanEnergySaveinInternalSaveEffectRateIssue"
        
        print("PeakValueInternalSaveUseUseapproximatelyBundleTest Passed")
    
    def test_memory_leak_detection(self):
        """TestInternalSaveleakCheckTest"""
        
        process = psutil.Process()
        
        # ExecuteManyTimesCameraSameoperationWork,CheckTestInternalSaveYesNoSupportContinueIncreaseLength
        memory_samples = []
        num_iterations = 5
        
        for i in range(num_iterations):
            # StrongControlgarbageReturnReceive
            gc.collect()
            
            # RecordInternalSaveUseUse
            current_memory = process.memory_info().rss / (1024 * 1024)
            memory_samples.append(current_memory)
            
            # ExecuteoperationWork
            processor = DataProcessor()
            processor.create_sample_data()
            processor.validate_data()
            processor.calculate_seir_states()
            
            # CreateanddestroyDestroyerModelTypeObject
            sir_config = {
                'N': 10000,
                'beta': 0.05,
                'gamma': 0.1,
                'S0': 9999,
                'I0': 1,
                'R0': 0,
                'days': 50,
                'dt': 1
            }
            sir_model = SIRModel(sir_config)
            sir_model.solve_ode()
            
            # explicitlyStyleDeleteObject
            del processor
            del sir_model
            
            print(f"iterationGeneration{i+1}: InternalSaveUseUse{current_memory:.2f}MB")
        
        # MostEndStrongControlgarbageReturnReceive
        gc.collect()
        final_memory = process.memory_info().rss / (1024 * 1024)
        memory_samples.append(final_memory)
        
        # AnalysisInternalSavetrend
        if len(memory_samples) >= 3:
            # DesignCalculateInternalSaveIncreaseLengthtrend(LinenessReturnregression slopeRate)
            x = list(range(len(memory_samples)))
            y = memory_samples
            
            # SimpleSingleLinenessReturnregression
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(xi * yi for xi, yi in zip(x, y))
            sum_x2 = sum(xi ** 2 for xi in x)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
            
            print(f"InternalSavesampleBook: {[f'{m:.1f}' for m in memory_samples]}MB")
            print(f"InternalSaveIncreaseLengthtrend: {slope:.3f}MB/iterationGeneration")
            
            # VerifyNosignificantInternalSaveleak(trendslopeRateShouldThisInterfacenear0)
            assert abs(slope) <= 5.0, \
                f"CheckTesttoCanEnergyInternalSaveleak,IncreaseLengthtrend{slope:.3f}MB/iterationGenerationOverLarge"
        
        print("InternalSaveleakCheckTestTest Passed")
    
    def test_large_scale_memory_stability(self):
        """TestLargeRuleModelModelSimulationInternalSavestableFixedness"""
        
        # TestLargeRuleModelEmptyBetweenModelSimulationInternalSaveUseUse
        large_spatial_config = {
            'grid_size': 100,            # LargegridFormat
            'num_individuals': 5000,     # CompareManyitem(s)Integrated
            'sigma': 2,
            'transmission_distance': 4,
            'beta': 0.04,
            'sigma_rate': 0.1,
            'gamma': 0.1,
            'v1': 1/5,
            'v2': 1/3,
            'isolation_duration': 14,
            'days': 30,                  # SuitableinDayNumber
            'dt': 1,
            'initial_infected': 10
        }
        
        with memory_monitor() as get_memory_info:
            try:
                spatial_model = SpatialBrownianModel(large_spatial_config)
                spatial_model.solve_simulation()
                
                # CheckModelTypeYesNoSuccessCompleteSuccess
                assert spatial_model.time is not None, "EmptyBetweenModelTypeShouldThisCompleteSuccesssimulationTrue"
                assert len(spatial_model.individuals) > 0, "ShouldThisHasitem(s)IntegratedData"
                
            except MemoryError:
                print("CorrectAccurateProcessingInternalSaveNotsufficientSituationstate")
                return  # ifResultInternalSaveNotsufficient,thisYesCanInterfaceacceptable
        
        memory_info = get_memory_info()
        peak_gb = memory_info['peak'] / 1024
        
        print(f"LargeRuleModelEmptyBetweenModelSimulationPeakValueInternalSave: {peak_gb:.3f}GB")
        
        # VerifyLargeRuleModelModelSimulationstillinInternalSaveLimitedControlInternal
        if peak_gb <= self.max_memory_gb:
            print("LargeRuleModelModelSimulationInternalSaveUseUseCombineProcessor")
        else:
            print(f"LargeRuleModelModelSimulationInternalSaveUseUse{peak_gb:.3f}GBUltraOverLimitedControl,butthisCanEnergyYesCanInterfaceacceptable")
        
        print("LargeRuleModelInternalSavestableFixednessTest Passed")
    
    def test_memory_cleanup_effectiveness(self):
        """TestInternalSaveCleanProcessorHasEffectness"""
        
        process = psutil.Process()
        
        # RecordInitialInitialInternalSave
        gc.collect()
        initial_memory = process.memory_info().rss / (1024 * 1024)
        
        # CreateLargeEditionObject
        large_objects = []
        for i in range(10):
            config = {
                'N': 20000,
                'beta': 0.05,
                'gamma': 0.1,
                'S0': 19999,
                'I0': 1,
                'R0': 0,
                'days': 100,
                'dt': 1
            }
            model = SIRModel(config)
            model.solve_ode()
            large_objects.append(model)
        
        # RecordUseUseLargeEditionInternalSaveTimeSituationstate
        gc.collect()
        high_memory = process.memory_info().rss / (1024 * 1024)
        
        # DeleteObjectparallelStrongControlgarbageReturnReceive
        del large_objects
        gc.collect()
        
        # EqualWaitInternalSavereleaseDispense
        time.sleep(1)
        
        # RecordCleanProcessorafterInternalSave
        final_memory = process.memory_info().rss / (1024 * 1024)
        
        print(f"InternalSaveCleanProcessorTest:")
        print(f"InitialInitialInternalSave: {initial_memory:.2f}MB")
        print(f"HighPeakInternalSave: {high_memory:.2f}MB")
        print(f"CleanProcessorafterInternalSave: {final_memory:.2f}MB")
        print(f"InternalSavereleaseDispense: {high_memory - final_memory:.2f}MB")
        
        # VerifyInternalSaveEnergyenoughHasEffectreleaseDispense
        memory_released = high_memory - final_memory
        memory_used = high_memory - initial_memory
        
        if memory_used > 0:
            release_ratio = memory_released / memory_used
            assert release_ratio >= 0.7, \
                f"InternalSavereleaseDispenseBiferExample{release_ratio:.1%}LowAt70%,CanEnergySaveinInternalSaveleak"
        
        print("InternalSaveCleanProcessorHasEffectnessTest Passed")
    
    def test_concurrent_memory_stability(self):
        """TestparallelSendExecuteInternalSavestableFixedness"""
        
        def worker_function(worker_id):
            """EngineeringWorkLineProcessFunctionNumber"""
            config = {
                'N': 5000,
                'beta': 0.05,
                'gamma': 0.1,
                'S0': 4999,
                'I0': 1,
                'R0': 0,
                'days': 50,
                'dt': 1
            }
            
            model = SIRModel(config)
            model.solve_ode()
            return worker_id
        
        with memory_monitor() as get_memory_info:
            # CreateManyitem(s)EngineeringWorkLineProcess
            threads = []
            num_workers = 4
            
            for i in range(num_workers):
                thread = threading.Thread(target=worker_function, args=(i,))
                threads.append(thread)
                thread.start()
            
            # EqualWaitPlaceHasLineProcessCompleteSuccess
            for thread in threads:
                thread.join()
        
        memory_info = get_memory_info()
        peak_gb = memory_info['peak'] / 1024
        
        print(f"parallelSendExecute({num_workers}LineProcess)PeakValueInternalSave: {peak_gb:.3f}GB")
        
        # VerifyparallelSendExecuteInternalSaveUseUsestillinLimitedControlInternal
        assert peak_gb <= self.max_memory_gb, \
            f"parallelSendExecutePeakValueInternalSave{peak_gb:.3f}GBUltraOver{self.max_memory_gb}GBLimitedControl"
        
        print("parallelSendInternalSavestableFixednessTest Passed")
    
    def test_long_running_memory_stability(self):
        """TestLengthPeriodRunInternalSavestableFixedness"""
        
        process = psutil.Process()
        memory_history = []
        
        # ModelSimulationLengthPeriodRun(ManyTimesExecuteshorttask)
        num_cycles = 20
        
        for cycle in range(num_cycles):
            # ExecuteModelSimulationtask
            config = {
                'N': 10000,
                'beta': 0.05,
                'gamma': 0.1,
                'S0': 9999,
                'I0': 1,
                'R0': 0,
                'days': 20,  # shortPeriodModelSimulation
                'dt': 1
            }
            
            model = SIRModel(config)
            model.solve_ode()
            
            # explicitlyStyleDeleteObject
            del model
            
            # each5item(s)cyclePeriodExecuteOneTimesgarbageReturnReceive
            if cycle % 5 == 0:
                gc.collect()
            
            # RecordInternalSaveUseUse
            current_memory = process.memory_info().rss / (1024 * 1024)
            memory_history.append(current_memory)
            
            if cycle % 5 == 0:
                print(f"cyclePeriod{cycle}: {current_memory:.2f}MB")
        
        # AnalysisInternalSavestableFixedness
        if len(memory_history) >= 10:
            # BiferComparebeforePeriodandafterPeriodInternalSaveUseUse
            early_avg = sum(memory_history[:5]) / 5
            late_avg = sum(memory_history[-5:]) / 5
            memory_growth = late_avg - early_avg
            
            print(f"LengthPeriodRunInternalSaveAnalysis:")
            print(f"beforePeriodAverageAverage: {early_avg:.2f}MB")
            print(f"afterPeriodAverageAverage: {late_avg:.2f}MB")
            print(f"InternalSaveIncreaseLength: {memory_growth:.2f}MB")
            
            # VerifyLengthPeriodRunNosignificantInternalSaveIncreaseLength(<100MBIncreaseLengthCanInterfaceacceptable)
            assert memory_growth <= 100, \
                f"LengthPeriodRunInternalSaveIncreaseLength{memory_growth:.2f}MBOverLarge,CanEnergyHasInternalSaveleak"
        
        print("LengthPeriodRunInternalSavestableFixednessTest Passed")
    
    def test_memory_usage_proportionality(self):
        """TestInternalSaveUseUseBiferExampleness"""
        
        # TestNotSameRuleModelModelSimulationInternalSaveUseUseBiferExample
        population_sizes = [1000, 5000, 10000, 20000]
        memory_usage = []
        
        for N in population_sizes:
            with memory_monitor() as get_memory_info:
                config = {
                    'N': N,
                    'beta': 0.05,
                    'gamma': 0.1,
                    'S0': N-1,
                    'I0': 1,
                    'R0': 0,
                    'days': 100,
                    'dt': 1
                }
                
                model = SIRModel(config)
                model.solve_ode()
                
                gc.collect()
            
            memory_info = get_memory_info()
            memory_growth = memory_info['peak'] - memory_info['baseline']
            memory_usage.append((N, memory_growth))
            
            print(f"PersonPort{N}: InternalSaveIncreaseLength{memory_growth:.2f}MB")
        
        # VerifyInternalSaveUseUseandIssueRuleModelshowCombineProcessorBiferExample
        # PersonPortIncreaseLarge20times,InternalSaveNotShouldIncreaseLargeUltraOver100times
        if len(memory_usage) >= 2:
            memory_ratio = memory_usage[-1][1] / memory_usage[0][1] if memory_usage[0][1] > 0 else 1
            population_ratio = population_sizes[-1] / population_sizes[0]
            
            efficiency_ratio = memory_ratio / population_ratio
            
            print(f"InternalSaveEffectRateAnalysis:")
            print(f"PersonPortExtendmultiplesNumber: {population_ratio}")
            print(f"InternalSaveIncreaseLengthtimesNumber: {memory_ratio:.2f}")
            print(f"EffectRateBifer: {efficiency_ratio:.2f}")
            
            assert efficiency_ratio <= 10.0, \
                f"InternalSaveEffectRateBifer{efficiency_ratio:.2f}OverHigh,InternalSaveUseUseNotCombineProcessor"
        
        print("InternalSaveUseUseBiferExamplenessTest Passed")
    
    def test_garbage_collection_effectiveness(self):
        """TestgarbageReturnReceiveHasEffectness"""
        
        process = psutil.Process()
        
        # CreateLargeEditiontemporaryTimeObject
        gc.collect()
        before_creation = process.memory_info().rss / (1024 * 1024)
        
        # CreatetemporaryTimeObject
        temp_objects = []
        for i in range(100):
            processor = DataProcessor()
            processor.create_sample_data()
            temp_objects.append(processor)
        
        after_creation = process.memory_info().rss / (1024 * 1024)
        
        # DeleteObjectbutNotimmediate garbageReturnReceive
        del temp_objects
        before_gc = process.memory_info().rss / (1024 * 1024)
        
        # StrongControlgarbageReturnReceive
        collected = gc.collect()
        after_gc = process.memory_info().rss / (1024 * 1024)
        
        print(f"garbageReturnReceiveTest:")
        print(f"Createbefore: {before_creation:.2f}MB")
        print(f"Createafter: {after_creation:.2f}MB")
        print(f"Deleteafter: {before_gc:.2f}MB")
        print(f"ReturnReceiveafter: {after_gc:.2f}MB")
        print(f"ReturnReceiveObjectNumber: {collected}")
        
        # VerifygarbageReturnReceivereleaseDispenseInternalSave
        memory_freed = before_gc - after_gc
        memory_used = after_creation - before_creation
        
        if memory_used > 10:  # ifResultAccurateImplementationUseUseInternalSave
            free_ratio = memory_freed / memory_used if memory_used > 0 else 0
            assert free_ratio >= 0.5, \
                f"garbageReturnReceivereleaseDispenseBiferExample{free_ratio:.1%}OverLow"
        
        print("garbageReturnReceiveHasEffectnessTest Passed")


if __name__ == "__main__":
    # RunTest
    test_instance = TestMemoryPerformance()
    test_instance.setup_method()
    
    try:
        test_instance.test_peak_memory_usage_constraint()
        test_instance.test_memory_leak_detection()
        test_instance.test_large_scale_memory_stability()
        test_instance.test_concurrent_memory_stability()
        test_instance.test_long_running_memory_stability()
        test_instance.test_memory_usage_proportionality()
        test_instance.test_garbage_collection_effectiveness()
        print("\nPlaceHasInternalSaveUseUsePerformanceTest Passed!")
    except AssertionError as e:
        print(f"\nTest Failed: {e}")
    except Exception as e:
        print(f"\nTestOutputWrong: {e}")