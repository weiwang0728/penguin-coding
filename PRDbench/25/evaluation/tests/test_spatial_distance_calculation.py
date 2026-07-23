# -*- coding: utf-8 -*-
"""
EmptyBetweenDistanceDistanceDesignCalculateUnit Test
TestSpatialBrownianModelCategoryinEmptyBetweenDistanceDistanceDesignCalculateFunction
"""

import pytest
import numpy as np
import os
import sys

# AddsrcDirectorytoPath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from models.spatial_brownian_model import SpatialBrownianModel, Individual


class TestSpatialDistanceCalculation:
    """EmptyBetweenDistanceDistanceDesignCalculateTestCategory"""
    
    def setup_method(self):
        """eachitem(s)TestOfficialMethodbeforeDesignSet"""
        # CreateOneitem(s)SimpleSingleConfigureUseAtTest
        test_config = {
            'grid_size': 50,
            'num_individuals': 100,
            'sigma': 2,
            'transmission_distance': 4,  # TraditionalSpreadDistanceDistanceThresholdValueas4
            'beta': 0.04,
            'sigma_rate': 0.1,
            'gamma': 0.1,
            'v1': 1/5,
            'v2': 1/3,
            'isolation_duration': 14,
            'days': 10,
            'dt': 1,
            'initial_infected': 5
        }
        self.model = SpatialBrownianModel(test_config)
        
    def test_spatial_distance_calculation_accuracy(self):
        """TestEmptyBetweenDistanceDistanceDesignCalculateStandardAccurateness
        
        Verify:
        1. EmptyBetweenDistanceDistanceDesignCalculateCorrectAccurate(OuEuclideanDistanceDistance)
        2. TraditionalSpreadDistanceDistanceThresholdValue4item(s)gridFormatSinglePositionNativeEffect
        3. UltraOverThresholdValueitem(s)IntegratedBetweenNotSendNativeTraditionalSpread
        """
        
        # CreateTestitem(s)Integrated
        ind1 = Individual(0, 0, 'I')  # InfectionInfectionErinNativePoint
        ind2 = Individual(3, 4, 'S')  # EasyInfectionErin(3,4)PositionSet
        ind3 = Individual(5, 0, 'S')  # EasyInfectionErin(5,0)PositionSet
        ind4 = Individual(0, 5, 'S')  # EasyInfectionErin(0,5)PositionSet
        
        # TestOuEuclideanDistanceDistanceDesignCalculateCorrectAccurateness
        # DistanceDistanceShouldThisYes sqrt((3-0)^2 + (4-0)^2) = sqrt(9+16) = sqrt(25) = 5
        distance1 = self.model.calculate_distance(ind1, ind2)
        expected_distance1 = np.sqrt((3-0)**2 + (4-0)**2)
        assert abs(distance1 - expected_distance1) < 1e-10, \
            f"DistanceDistanceDesignCalculateError:Periodexpected{expected_distance1},ImplementationInternational{distance1}"
        assert abs(distance1 - 5.0) < 1e-10, \
            f"ToolIntegratedDistanceDistanceDesignCalculateError:Periodexpected5.0,ImplementationInternational{distance1}"
        
        # TestotherDistanceDistanceDesignCalculate
        distance2 = self.model.calculate_distance(ind1, ind3)  # ShouldThisYes5
        distance3 = self.model.calculate_distance(ind1, ind4)  # ShouldThisYes5
        
        assert abs(distance2 - 5.0) < 1e-10, \
            f"DistanceDistanceDesignCalculateError:Periodexpected5.0,ImplementationInternational{distance2}"
        assert abs(distance3 - 5.0) < 1e-10, \
            f"DistanceDistanceDesignCalculateError:Periodexpected5.0,ImplementationInternational{distance3}"
        
        # VerifyTraditionalSpreadDistanceDistanceThresholdValueDesignSet
        assert self.model.transmission_distance == 4, \
            f"TraditionalSpreadDistanceDistanceThresholdValueShouldas4,ImplementationInternationalas{self.model.transmission_distance}"
        
        print("EmptyBetweenDistanceDistanceDesignCalculateStandardAccuratenessTest Passed")
    
    def test_transmission_distance_threshold(self):
        """TestTraditionalSpreadDistanceDistanceThresholdValueNativeEffectness"""
        
        # CreateTestscenario:Oneitem(s)InfectionInfectionErandManyitem(s)EasyInfectionEr
        infected = Individual(10, 10, 'I')  # InfectionInfectionEr
        
        # inThresholdValueInternalEasyInfectionEr(DistanceDistance < 4)
        close_susceptible1 = Individual(10, 13, 'S')  # DistanceDistance = 3
        close_susceptible2 = Individual(12, 12, 'S')  # DistanceDistance = sqrt(8) ≈ 2.83
        
        # inThresholdValueboundaryBoundaryEasyInfectionEr(DistanceDistance = 4)
        boundary_susceptible = Individual(10, 14, 'S')  # DistanceDistance = 4
        
        # UltraOverThresholdValueEasyInfectionEr(DistanceDistance > 4)
        far_susceptible1 = Individual(10, 15, 'S')  # DistanceDistance = 5
        far_susceptible2 = Individual(15, 15, 'S')  # DistanceDistance = sqrt(50) ≈ 7.07
        
        # VerifyDistanceDistanceDesignCalculate
        assert self.model.calculate_distance(infected, close_susceptible1) == 3.0
        assert abs(self.model.calculate_distance(infected, close_susceptible2) - np.sqrt(8)) < 1e-10
        assert self.model.calculate_distance(infected, boundary_susceptible) == 4.0
        assert self.model.calculate_distance(infected, far_susceptible1) == 5.0
        assert abs(self.model.calculate_distance(infected, far_susceptible2) - np.sqrt(50)) < 1e-10
        
        # VerifyTraditionalSpreadDistanceDistanceThresholdValuelogic
        # inThresholdValueInternalitem(s)IntegratedShouldThisCanEnergybeTraditionalSpread(DistanceDistance <= 4)
        assert self.model.calculate_distance(infected, close_susceptible1) <= self.model.transmission_distance
        assert self.model.calculate_distance(infected, close_susceptible2) <= self.model.transmission_distance
        assert self.model.calculate_distance(infected, boundary_susceptible) <= self.model.transmission_distance
        
        # UltraOverThresholdValueitem(s)IntegratedNotShouldThisbeTraditionalSpread(DistanceDistance > 4)
        assert self.model.calculate_distance(infected, far_susceptible1) > self.model.transmission_distance
        assert self.model.calculate_distance(infected, far_susceptible2) > self.model.transmission_distance
        
        print("TraditionalSpreadDistanceDistanceThresholdValueTest Passed")
    
    def test_distance_calculation_edge_cases(self):
        """TestDistanceDistanceDesignCalculateboundaryBoundarySituationstate"""
        
        # TestCameraSamePositionSetitem(s)Integrated(DistanceDistanceShouldas0)
        ind1 = Individual(5, 5, 'I')
        ind2 = Individual(5, 5, 'S')
        distance = self.model.calculate_distance(ind1, ind2)
        assert distance == 0.0, f"CameraSamePositionSetDistanceDistanceShouldas0,ImplementationInternationalas{distance}"
        
        # TestMostLargeDistanceDistance(gridFormatforangleLine)
        ind3 = Individual(0, 0, 'I')
        ind4 = Individual(50, 50, 'S')  # gridFormatLargeSmallas50
        max_distance = self.model.calculate_distance(ind3, ind4)
        expected_max = np.sqrt(50**2 + 50**2)
        assert abs(max_distance - expected_max) < 1e-10, \
            f"MostLargeDistanceDistanceDesignCalculateError:Periodexpected{expected_max},ImplementationInternational{max_distance}"
        
        # TestNegativecoordinateMark(althoughinImplementationInternationalModelTypeinNotwillOutputImplementation,butTestFunctionNumberrobustness)
        ind5 = Individual(-2, -3, 'I')
        ind6 = Individual(1, 1, 'S')
        distance_negative = self.model.calculate_distance(ind5, ind6)
        expected_negative = np.sqrt((1-(-2))**2 + (1-(-3))**2)  # sqrt(9+16) = 5
        assert abs(distance_negative - expected_negative) < 1e-10, \
            f"NegativecoordinateMarkDistanceDistanceDesignCalculateError:Periodexpected{expected_negative},ImplementationInternational{distance_negative}"
        
        print("boundaryBoundarySituationstateTest Passed")
    
    def test_transmission_threshold_in_simulation_context(self):
        """TestinsimulationTrueonunderTextinTraditionalSpreadThresholdValueCorrectAccurateShouldUse"""
        
        # DesignSettwoitem(s)item(s)Integrated:Oneitem(s)InfectionInfectionEr,Oneitem(s)EasyInfectionEr
        self.model.individuals = [
            Individual(10, 10, 'I'),  # InfectionInfectionEr
            Individual(10, 15, 'S')   # EasyInfectionEr,DistanceDistanceas5 > 4(ThresholdValue)
        ]
        
        # RecordInitialInitialStatus
        initial_susceptible_state = self.model.individuals[1].state
        assert initial_susceptible_state == 'S', "InitialInitialStatusShouldasEasyInfectionEr"
        
        # ModelSimulationOneTimesTraditionalSpreadStepstep
        # becauseAtDistanceDistanceUltraOverThresholdValue,NotShouldThisSendNativeTraditionalSpread
        original_beta = self.model.beta
        self.model.beta = 1.0  # DesignSetveryHighTraditionalSpreadRate,AccurateProtectionifResultDistanceDistanceallowthenwillTraditionalSpread
        
        # ExecuteTraditionalSpreadStepstepManyTimes,AccurateProtectionNotwillSendNativeTraditionalSpread
        for _ in range(100):  # ExecuteManyTimestoexcludeRemoverandomMachineness
            self.model.transmission_step()
            # becauseAtDistanceDistanceUltraOverThresholdValue,EasyInfectionErStatusNotShouldChangeChange
            assert self.model.individuals[1].state == 'S', \
                "UltraOverTraditionalSpreadDistanceDistanceThresholdValueitem(s)IntegratedNotShouldbeInfectionInfection"
        
        # ResumeRecoveryNativeInitialTraditionalSpreadRate
        self.model.beta = original_beta
        
        # ImplementationinTestinThresholdValueInternalSituationstate
        self.model.individuals[1].x = 10
        self.model.individuals[1].y = 13  # DistanceDistanceas3 < 4(ThresholdValue)
        self.model.individuals[1].state = 'S'  # WeightSetasEasyInfectionEr
        
        # VerifyDistanceDistanceAccurateImplementationinThresholdValueInternal
        distance = self.model.calculate_distance(self.model.individuals[0], self.model.individuals[1])
        assert distance <= self.model.transmission_distance, \
            f"Testitem(s)IntegratedDistanceDistance{distance}ShouldThisSmallAtEqualAtThresholdValue{self.model.transmission_distance}"
        
        print("simulationTrueonunderTextinTraditionalSpreadThresholdValueTest Passed")
    
    def test_euclidean_distance_formula(self):
        """VerifyOuEuclideanDistanceDistanceOfficeStyleCorrectAccurateImplementationImplementation"""
        
        # CreateManyitem(s)TestCaseExample
        test_cases = [
            # (x1, y1, x2, y2, expected_distance)
            (0, 0, 0, 0, 0.0),           # SameOnePoint
            (0, 0, 1, 0, 1.0),           # waterAverageDistanceDistance
            (0, 0, 0, 1, 1.0),           # verticalDirectDistanceDistance
            (0, 0, 1, 1, np.sqrt(2)),    # forangleLine
            (0, 0, 3, 4, 5.0),           # 3-4-5DirectangleSamangleshape
            (1, 2, 4, 6, 5.0),           # anotherOneitem(s)3-4-5Samangleshape
            (10.5, 20.3, 15.7, 25.9, np.sqrt((15.7-10.5)**2 + (25.9-20.3)**2))  # SmallNumbercoordinateMark
        ]
        
        for x1, y1, x2, y2, expected in test_cases:
            ind1 = Individual(x1, y1, 'I')
            ind2 = Individual(x2, y2, 'S')
            
            calculated = self.model.calculate_distance(ind1, ind2)
            assert abs(calculated - expected) < 1e-10, \
                f"DistanceDistanceDesignCalculateError:Point({x1},{y1})to({x2},{y2}),Periodexpected{expected},ImplementationInternational{calculated}"
        
        print("OuEuclideanDistanceDistanceOfficeStyleVerifyPass")


if __name__ == "__main__":
    # RunTest
    test_instance = TestSpatialDistanceCalculation()
    test_instance.setup_method()
    
    try:
        test_instance.test_spatial_distance_calculation_accuracy()
        test_instance.test_transmission_distance_threshold()
        test_instance.test_distance_calculation_edge_cases()
        test_instance.test_transmission_threshold_in_simulation_context()
        test_instance.test_euclidean_distance_formula()
        print("\nPlaceHasEmptyBetweenDistanceDistanceDesignCalculateTest Passed!")
    except AssertionError as e:
        print(f"\nTest Failed: {e}")
    except Exception as e:
        print(f"\nTestOutputWrong: {e}")