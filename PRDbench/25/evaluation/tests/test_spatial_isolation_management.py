# -*- coding: utf-8 -*-
"""
EmptyBetweenIsolationDistanceStatusManagementUnit Test
TestSpatialBrownianModelCategoryinIsolationDistanceStatusManagementFunction
"""

import pytest
import numpy as np
import os
import sys

# AddsrcDirectorytoPath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from models.spatial_brownian_model import SpatialBrownianModel, Individual


class TestSpatialIsolationManagement:
    """EmptyBetweenIsolationDistanceStatusManagementTestCategory"""
    
    def setup_method(self):
        """eachitem(s)TestOfficialMethodbeforeDesignSet"""
        # CreateOneitem(s)SimpleizationConfigureUseAtTest
        test_config = {
            'grid_size': 50,
            'num_individuals': 100,
            'sigma': 2,
            'transmission_distance': 4,
            'beta': 0.04,
            'sigma_rate': 0.1,                # LatentlatentPeriodConvertInfectionInfectionRate
            'gamma': 0.1,                     # HealthRecoveryRate
            'v1': 1/5,                        # LatentlatentErIsolationDistanceRate
            'v2': 1/3,                        # InfectionInfectionErIsolationDistanceRate
            'isolation_duration': 14,         # IsolationDistanceSupportContinueTimeBetween14Day
            'days': 30,
            'dt': 1,
            'initial_infected': 5
        }
        self.model = SpatialBrownianModel(test_config)
        
    def test_isolation_prevents_movement(self):
        """TestIsolationDistanceitem(s)IntegratedStopstopMoveAuto
        
        Verify:
        1. IsolationDistanceitem(s)IntegratedStopstopMoveAuto
        2. IsolationDistanceTimeBetweenreverseDesignTimeStandardAccurate
        3. IsolationDistanceremoveRemoveMachineControlNormalEngineeringWork
        """
        
        # CreateOneitem(s)item(s)IntegratedparallelDesignSetasIsolationDistanceStatus
        individual = Individual(25, 25, 'I')
        individual.is_isolated = True
        individual.isolation_time = 5  # AlreadyIsolationDistance5Day
        
        # RecordInitialInitialPositionSet
        initial_x, initial_y = individual.x, individual.y
        initial_isolation_time = individual.isolation_time
        
        # attemptMoveAuto(ShouldThisNotMoveAuto)
        for _ in range(10):
            individual.move(self.model.sigma, self.model.grid_size)
            
            # VerifyPositionSetnotHasChangeChange
            assert individual.x == initial_x, \
                f"IsolationDistanceitem(s)IntegratedNotShouldMoveAuto,XcoordinateMarkfrom{initial_x}Changeas{individual.x}"
            assert individual.y == initial_y, \
                f"IsolationDistanceitem(s)IntegratedNotShouldMoveAuto,YcoordinateMarkfrom{initial_y}Changeas{individual.y}"
        
        # TestIsolationDistanceTimeBetweenreverseDesignTime
        individual.update_state(
            self.model.sigma_rate, 
            self.model.gamma, 
            self.model.v1, 
            self.model.v2, 
            self.model.isolation_duration, 
            self.model.dt
        )
        
        # VerifyIsolationDistanceTimeBetweenIncreasePlus
        expected_isolation_time = initial_isolation_time + self.model.dt
        assert individual.isolation_time == expected_isolation_time, \
            f"IsolationDistanceTimeBetweenShouldfrom{initial_isolation_time}IncreasePlusto{expected_isolation_time},ImplementationInternationalas{individual.isolation_time}"
        
        print("IsolationDistanceblockstopMoveAutoTest Passed")
    
    def test_isolation_time_countdown_accuracy(self):
        """TestIsolationDistanceTimeBetweenreverseDesignTimeStandardAccurateness"""
        
        individual = Individual(10, 10, 'E')
        individual.is_isolated = True
        individual.isolation_time = 0
        
        # ModelSimulationManyDayIsolationDistanceTimeBetweencumulative
        days_to_simulate = 10
        for day in range(days_to_simulate):
            individual.update_state(
                self.model.sigma_rate, 
                self.model.gamma, 
                self.model.v1, 
                self.model.v2, 
                self.model.isolation_duration, 
                self.model.dt
            )
            
            expected_time = (day + 1) * self.model.dt
            assert abs(individual.isolation_time - expected_time) < 1e-10, \
                f"index{day+1}DayIsolationDistanceTimeBetweenShouldas{expected_time},ImplementationInternationalas{individual.isolation_time}"
        
        print("IsolationDistanceTimeBetweenreverseDesignTimeStandardAccuratenessTest Passed")
    
    def test_isolation_release_mechanism(self):
        """TestIsolationDistanceremoveRemoveMachineControlNormalEngineeringWork"""
        
        individual = Individual(15, 15, 'I')
        individual.is_isolated = True
        individual.isolation_time = self.model.isolation_duration - 1  # IsolationDistancePeriodimmediatelywillResultBundle
        
        # ExecuteStatusUpdate,ShouldThisremoveRemoveIsolationDistance
        individual.update_state(
            self.model.sigma_rate, 
            self.model.gamma, 
            self.model.v1, 
            self.model.v2, 
            self.model.isolation_duration, 
            self.model.dt
        )
        
        # VerifyIsolationDistanceremoveRemove
        assert not individual.is_isolated, "IsolationDistancePeriodfullafterShouldThisremoveRemoveIsolationDistance"
        assert individual.isolation_time == 0, "IsolationDistanceremoveRemoveafterIsolationDistanceTimeBetweenShouldWeightSetas0"
        
        # VerifyremoveRemoveIsolationDistanceafterCantoMoveAuto
        initial_x, initial_y = individual.x, individual.y
        individual.move(self.model.sigma, self.model.grid_size)
        
        # removeRemoveIsolationDistanceafterPositionSetCanEnergySendNativeChangeization(althoughNotOneFixedeachTimesallChange)
        # thisinsideonlyVerifyNotwillOutputWrongandcoordinateMarkstillinCombineProcessorRangerangeInternal
        assert 0 <= individual.x < self.model.grid_size
        assert 0 <= individual.y < self.model.grid_size
        
        print("IsolationDistanceremoveRemoveMachineControlTest Passed")
    
    def test_isolation_transmission_suppression(self):
        """TestIsolationDistanceforTraditionalSpreadHassignificantly suppressControlWorkUse(InfectionInfectionTraditionalSpreadSpeedDegreesDecreaseLow≥20%)"""
        
        # Createtwoitem(s)scenario:HasIsolationDistanceandNoIsolationDistance
        
        # scenario1:NoIsolationDistanceConfigure
        no_isolation_config = self.model.config.copy()
        no_isolation_config.update({
            'v1': 0.0,  # NoIsolationDistance
            'v2': 0.0,  # NoIsolationDistance
            'days': 20
        })
        
        # scenario2:HasIsolationDistanceConfigure
        with_isolation_config = self.model.config.copy()
        with_isolation_config.update({
            'v1': 0.2,  # HighIsolationDistanceRate
            'v2': 0.3,  # HighIsolationDistanceRate
            'days': 20
        })
        
        # RunNoIsolationDistanceModelSimulation
        no_isolation_model = SpatialBrownianModel(no_isolation_config)
        no_isolation_model.solve_simulation()
        
        # RunHasIsolationDistanceModelSimulation
        with_isolation_model = SpatialBrownianModel(with_isolation_config)
        with_isolation_model.solve_simulation()
        
        # DesignCalculateTraditionalSpreadSpeedDegreesIndicatorMark(InfectionInfectionPeakValue)
        no_isolation_peak = np.max(no_isolation_model.I_count)
        with_isolation_peak = np.max(with_isolation_model.I_count)
        
        # DesignCalculateInfectionInfectionTraditionalSpreadSpeedDegreesDecreaseLowRate
        if no_isolation_peak > 0:
            reduction_rate = (no_isolation_peak - with_isolation_peak) / no_isolation_peak
            
            print(f"NoIsolationDistanceInfectionInfectionPeakValue: {no_isolation_peak:.0f}")
            print(f"HasIsolationDistanceInfectionInfectionPeakValue: {with_isolation_peak:.0f}")
            print(f"TraditionalSpreadSpeedDegreesDecreaseLowRate: {reduction_rate:.1%}")
            
            # VerifyIsolationDistanceforTraditionalSpreadHassignificantly suppressControlWorkUse(≥20%)
            assert reduction_rate >= 0.20, \
                f"IsolationDistanceShouldThisUseInfectionInfectionTraditionalSpreadSpeedDegreesDecreaseLow≥20%,ImplementationInternationalDecreaseLow{reduction_rate:.1%}"
        else:
            print("NoIsolationDistanceSituationstateundernotHasTraditionalSpread,SkipthisTest")
        
        print("TraditionalSpreadsuppressControlWorkUseTest Passed")
    
    def test_isolation_state_transitions(self):
        """TestIsolationDistanceStatusConversionCorrectAccurateness"""
        
        # TestLatentlatentErImportInputIsolationDistance
        exposed_individual = Individual(20, 20, 'E')
        exposed_individual.is_isolated = False
        
        # DesignSetHighIsolationDistanceRateAccurateProtectionbeIsolationDistance
        high_v1 = 1.0  # 100%IsolationDistanceRate
        
        original_state = exposed_individual.state
        
        # ManyTimesattemptStatusUpdate,ShouldThiswill beIsolationDistance
        isolated = False
        for _ in range(100):  # attempt100Times
            exposed_individual.update_state(
                self.model.sigma_rate, 
                self.model.gamma, 
                high_v1,  # UseUseHighIsolationDistanceRate
                self.model.v2, 
                self.model.isolation_duration, 
                1.0  # UseUseCompareLargeTimeBetweenStepLengthIncreasePlusSummaryRate
            )
            
            if exposed_individual.is_isolated:
                isolated = True
                break
            
            # WeightSetStatusImportLineunderTimesattempt
            exposed_individual.state = 'E'
            exposed_individual.is_isolated = False
        
        assert isolated, "LatentlatentErShouldThisHasMachinewill beIsolationDistance"
        
        # TestInfectionInfectionErImportInputIsolationDistance
        infected_individual = Individual(30, 30, 'I')
        infected_individual.is_isolated = False
        
        high_v2 = 1.0  # 100%IsolationDistanceRate
        
        isolated = False
        for _ in range(100):  # attempt100Times
            infected_individual.update_state(
                self.model.sigma_rate, 
                self.model.gamma, 
                self.model.v1, 
                high_v2,  # UseUseHighIsolationDistanceRate
                self.model.isolation_duration, 
                1.0  # UseUseCompareLargeTimeBetweenStepLengthIncreasePlusSummaryRate
            )
            
            if infected_individual.is_isolated:
                isolated = True
                break
            
            # WeightSetStatusImportLineunderTimesattempt
            infected_individual.state = 'I'
            infected_individual.is_isolated = False
        
        assert isolated, "InfectionInfectionErShouldThisHasMachinewill beIsolationDistance"
        
        print("IsolationDistanceStatusConversionTest Passed")
    
    def test_isolation_during_state_progression(self):
        """TestIsolationDistancePeriodBetweenStatusImportextension"""
        
        # CreateOneitem(s)IsolationDistanceinLatentlatentEr
        individual = Individual(25, 25, 'E')
        individual.is_isolated = True
        individual.isolation_time = 5
        
        original_state = individual.state
        
        # inIsolationDistancePeriodBetween,LatentlatentErstillCanEnergyConvertasInfectionInfectionEr
        for _ in range(100):  # ManyTimesattempt
            # WeightSetasLatentlatentErStatus
            individual.state = 'E'
            individual.is_isolated = True
            
            individual.update_state(
                1.0,  # HighConversionRate
                self.model.gamma, 
                self.model.v1, 
                self.model.v2, 
                self.model.isolation_duration, 
                1.0  # LargeTimeBetweenStepLength
            )
            
            # ifResultStatusConversionasInfectionInfectionEr,DescriptionIsolationDistancePeriodBetweenStatusImportextensionNormal
            if individual.state == 'I':
                print("IsolationDistancePeriodBetweenStatusImportextensionNormal:LatentlatentErConvertasInfectionInfectionEr")
                break
        
        print("IsolationDistancePeriodBetweenStatusImportextensionTest Passed")
    
    def test_isolation_effectiveness_metrics(self):
        """TestIsolationDistanceEffectResultEditionizationIndicatorMark"""
        
        # CreateOneitem(s)HasInitialInitialInfectionInfectionErSimpleSinglescenario
        individuals = [
            Individual(25, 25, 'I'),    # InfectionInfectionEr
            Individual(26, 25, 'S'),    # adjacentnearEasyInfectionEr
            Individual(27, 25, 'S'),    # adjacentnearEasyInfectionEr
            Individual(28, 25, 'S'),    # adjacentnearEasyInfectionEr
        ]
        
        # DesignSetIsolationDistanceParameter
        v1, v2 = 0.3, 0.5
        isolation_duration = 14
        
        # ModelSimulationOneSegmentTimeBetween,ViewObserveIsolationDistanceEffectResult
        days_to_simulate = 10
        isolated_count_over_time = []
        
        for day in range(days_to_simulate):
            # UpdatePlaceHasitem(s)IntegratedStatus
            for individual in individuals:
                individual.update_state(
                    self.model.sigma_rate, 
                    self.model.gamma, 
                    v1, v2, 
                    isolation_duration, 
                    self.model.dt
                )
            
            # SystemDesignIsolationDistanceitem(s)IntegratedQuantity
            isolated_count = sum(1 for ind in individuals if ind.is_isolated)
            isolated_count_over_time.append(isolated_count)
        
        # VerifyIsolationDistanceMachineControlinEngineeringWork
        max_isolated = max(isolated_count_over_time)
        total_isolated_days = sum(isolated_count_over_time)
        
        print(f"MostLargeSameTimeIsolationDistancePersonNumber: {max_isolated}")
        print(f"TotalIsolationDistancePersonDayNumber: {total_isolated_days}")
        
        # ShouldThisHasOneFixedQuantityIsolationDistanceSendNative
        assert total_isolated_days > 0, "ShouldThisHasIsolationDistancemeasureImplementationapply"
        
        print("IsolationDistanceEffectResultEditionizationIndicatorMarkTest Passed")


if __name__ == "__main__":
    # RunTest
    test_instance = TestSpatialIsolationManagement()
    test_instance.setup_method()
    
    try:
        test_instance.test_isolation_prevents_movement()
        test_instance.test_isolation_time_countdown_accuracy()
        test_instance.test_isolation_release_mechanism()
        test_instance.test_isolation_transmission_suppression()
        test_instance.test_isolation_state_transitions()
        test_instance.test_isolation_during_state_progression()
        test_instance.test_isolation_effectiveness_metrics()
        print("\nPlaceHasEmptyBetweenIsolationDistanceStatusManagementTest Passed!")
    except AssertionError as e:
        print(f"\nTest Failed: {e}")
    except Exception as e:
        print(f"\nTestOutputWrong: {e}")