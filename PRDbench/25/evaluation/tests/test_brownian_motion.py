# -*- coding: utf-8 -*-
"""
DistributionrandomSportsitem(s)IntegratedMoveAutoUnit Test
TestIndividualCategoryinDistributionrandomSportsMoveAutoFunction
"""

import pytest
import numpy as np
import os
import sys
from scipy import stats

# AddsrcDirectorytoPath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from models.spatial_brownian_model import Individual


class TestBrownianMotion:
    """DistributionrandomSportsTestCategory"""
    
    def setup_method(self):
        """eachitem(s)TestOfficialMethodbeforeDesignSet"""
        self.grid_size = 50
        self.sigma = 2  # DistributionrandomSportsStrongDegrees
        
    def test_brownian_motion_characteristics(self):
        """TestDistributionrandomSportsSpecialness
        
        Verify:
        1. item(s)IntegratedEmptyBetweenMoveAutoSymbolCombineDistributionrandomSportsSpecialness(randomMachinewalk)
        2. MoveAutoDistanceDistanceDivideDistributionCombineProcessor
        3. SportsStrongDegreesParameterNativeEffect
        """
        
        # Createitem(s)IntegratedingridFormatinCore
        individual = Individual(25, 25, 'S')
        initial_x, initial_y = individual.x, individual.y
        
        # RecordManyTimesMoveAutoPositionSetChangeization
        num_steps = 1000
        x_displacements = []
        y_displacements = []
        distances = []
        
        for _ in range(num_steps):
            prev_x, prev_y = individual.x, individual.y
            individual.move(self.sigma, self.grid_size)
            
            # DesignCalculatePositionMove
            dx = individual.x - prev_x
            dy = individual.y - prev_y
            distance = np.sqrt(dx**2 + dy**2)
            
            x_displacements.append(dx)
            y_displacements.append(dy)
            distances.append(distance)
        
        # ConversionasnumpyArrayPortableAtAnalysis
        x_displacements = np.array(x_displacements)
        y_displacements = np.array(y_displacements)
        distances = np.array(distances)
        
        # VerifyDistributionrandomSportsSpecialness
        # 1. PositionMoveAverageValueShouldThisInterfacenear0(randomMachinewalkSpecialness)
        x_mean = np.mean(x_displacements)
        y_mean = np.mean(y_displacements)
        
        assert abs(x_mean) < 0.2, f"XOfficialDirectionPositionMoveAverageValueShouldInterfacenear0,ImplementationInternationalas{x_mean}"
        assert abs(y_mean) < 0.2, f"YOfficialDirectionPositionMoveAverageValueShouldInterfacenear0,ImplementationInternationalas{y_mean}"
        
        # 2. PositionMoveMarkStandardDifferenceShouldThisandDesignFixedsigmaCameraRelated
        x_std = np.std(x_displacements)
        y_std = np.std(y_displacements)
        
        # allow20%errorDifferenceRangerange
        expected_std = self.sigma
        assert abs(x_std - expected_std) / expected_std < 0.2, \
            f"XOfficialDirectionMarkStandardDifferenceShouldInterfacenear{expected_std},ImplementationInternationalas{x_std}"
        assert abs(y_std - expected_std) / expected_std < 0.2, \
            f"YOfficialDirectionMarkStandardDifferenceShouldInterfacenear{expected_std},ImplementationInternationalas{y_std}"
        
        # 3. VerifyPositionMoveDivideDistributionInterfacenearCorrectstateDivideDistribution(Kolmogorov-SmirnovCheckExperience)
        # forXOfficialDirectionPositionMoveImportLineCorrectstatenessCheckExperience
        _, p_value_x = stats.kstest(x_displacements, lambda x: stats.norm.cdf(x, 0, self.sigma))
        _, p_value_y = stats.kstest(y_displacements, lambda x: stats.norm.cdf(x, 0, self.sigma))
        
        # pValueShouldThisLargeAt0.01(95%SetsignalDegreesunderNotrejectCorrectstateDivideDistributionFalseDesign)
        assert p_value_x > 0.01, f"XOfficialDirectionPositionMoveNotSymbolCombineCorrectstateDivideDistribution,pValue={p_value_x}"
        assert p_value_y > 0.01, f"YOfficialDirectionPositionMoveNotSymbolCombineCorrectstateDivideDistribution,pValue={p_value_y}"
        
        print("DistributionrandomSportsSpecialnessVerifyPass")
    
    def test_movement_distance_distribution(self):
        """TestMoveAutoDistanceDistanceDivideDistributionCombineProcessorness"""
        
        individual = Individual(25, 25, 'S')
        num_steps = 500
        distances = []
        
        for _ in range(num_steps):
            prev_x, prev_y = individual.x, individual.y
            individual.move(self.sigma, self.grid_size)
            
            distance = np.sqrt((individual.x - prev_x)**2 + (individual.y - prev_y)**2)
            distances.append(distance)
        
        distances = np.array(distances)
        
        # VerifyDistanceDistanceDivideDistributionSpecialness
        # 1. AverageAverageMoveAutoDistanceDistanceShouldThisinCombineProcessorRangerangeInternal
        mean_distance = np.mean(distances)
        expected_mean = self.sigma * np.sqrt(2)  # ProcessorreportPeriodexpectedValue
        
        assert abs(mean_distance - expected_mean) / expected_mean < 0.3, \
            f"AverageAverageMoveAutoDistanceDistanceShouldInterfacenear{expected_mean},ImplementationInternationalas{mean_distance}"
        
        # 2. MoveAutoDistanceDistanceShouldThisallYesnonNegative
        assert np.all(distances >= 0), "MoveAutoDistanceDistanceShouldThisallYesnonNegative"
        
        # 3. MostLargeMoveAutoDistanceDistanceShouldThisinCombineProcessorRangerangeInternal(NotShouldThisOverLarge)
        max_distance = np.max(distances)
        reasonable_max = self.sigma * 6  # 6timesMarkStandardDifferenceInternal
        
        assert max_distance <= reasonable_max, \
            f"MostLargeMoveAutoDistanceDistance{max_distance}UltraOverCombineProcessorRangerange{reasonable_max}"
        
        print("MoveAutoDistanceDistanceDivideDistributionTest Passed")
    
    def test_motion_intensity_parameter_effect(self):
        """TestSportsStrongDegreesParameterShadowResponse"""
        
        # TestNotSamesigmaValue
        sigma_values = [0.5, 1.0, 2.0, 4.0]
        results = {}
        
        for sigma in sigma_values:
            individual = Individual(25, 25, 'S')
            distances = []
            
            # ExecuteMoveAutoparallelRecordDistanceDistance
            for _ in range(200):
                prev_x, prev_y = individual.x, individual.y
                individual.move(sigma, self.grid_size)
                distance = np.sqrt((individual.x - prev_x)**2 + (individual.y - prev_y)**2)
                distances.append(distance)
            
            results[sigma] = {
                'mean_distance': np.mean(distances),
                'std_distance': np.std(distances)
            }
        
        # VerifysigmaParameterShadowResponse
        # UpdateLargesigmaShouldThisleadCauseUpdateLargeAverageAverageMoveAutoDistanceDistance
        for i in range(len(sigma_values) - 1):
            sigma1 = sigma_values[i]
            sigma2 = sigma_values[i + 1]
            
            mean1 = results[sigma1]['mean_distance']
            mean2 = results[sigma2]['mean_distance']
            
            assert mean2 > mean1, \
                f"UpdateLargesigma({sigma2})ShouldThisMadeNativeUpdateLargeAverageAverageMoveAutoDistanceDistance,but{mean2} <= {mean1}"
        
        print("SportsStrongDegreesParameterEffectResultTest Passed")
    
    def test_grid_boundary_constraints(self):
        """TestgridFormatboundaryBoundaryapproximatelyBundle"""
        
        # TestboundaryBoundarySituationstate
        test_cases = [
            (0, 0),           # leftunderangle
            (49, 49),         # rightonangle(grid_size-1)
            (0, 25),          # leftboundaryBoundary
            (49, 25),         # rightboundaryBoundary
            (25, 0),          # underboundaryBoundary
            (25, 49)          # onboundaryBoundary
        ]
        
        for start_x, start_y in test_cases:
            individual = Individual(start_x, start_y, 'S')
            
            # ExecuteManyTimesMoveAuto
            for _ in range(100):
                individual.move(self.sigma, self.grid_size)
                
                # Verifyitem(s)IntegratedInitialEndingridFormatRangerangeInternal
                assert 0 <= individual.x < self.grid_size, \
                    f"item(s)IntegratedXcoordinateMark{individual.x}UltraOutputgridFormatRangerange[0, {self.grid_size})"
                assert 0 <= individual.y < self.grid_size, \
                    f"item(s)IntegratedYcoordinateMark{individual.y}UltraOutputgridFormatRangerange[0, {self.grid_size})"
        
        print("gridFormatboundaryBoundaryapproximatelyBundleTest Passed")
    
    def test_isolation_prevents_movement(self):
        """TestIsolationDistanceStatusblockstopMoveAuto"""
        
        # CreateOneitem(s)item(s)IntegratedparallelDesignSetasIsolationDistanceStatus
        individual = Individual(25, 25, 'I')
        individual.is_isolated = True
        
        # RecordInitialInitialPositionSet
        initial_x, initial_y = individual.x, individual.y
        
        # attemptMoveAutoManyTimes
        for _ in range(100):
            individual.move(self.sigma, self.grid_size)
            
            # VerifyPositionSetnotHasChangeChange
            assert individual.x == initial_x, \
                f"IsolationDistanceitem(s)IntegratedNotShouldMoveAuto,XcoordinateMarkfrom{initial_x}Changeas{individual.x}"
            assert individual.y == initial_y, \
                f"IsolationDistanceitem(s)IntegratedNotShouldMoveAuto,YcoordinateMarkfrom{initial_y}Changeas{individual.y}"
        
        # TestremoveRemoveIsolationDistanceafterCantoMoveAuto
        individual.is_isolated = False
        individual.move(self.sigma, self.grid_size)
        
        # removeRemoveIsolationDistanceafterPositionSetCanEnergySendNativeChangeization(althoughNotOneFixedeachTimesallChange)
        # thisinsideonlyVerifyNotwillOutputWrong
        assert 0 <= individual.x < self.grid_size
        assert 0 <= individual.y < self.grid_size
        
        print("IsolationDistanceblockstopMoveAutoTest Passed")
    
    def test_random_walk_properties(self):
        """TestrandomMachinewalkSpecialness"""
        
        individual = Individual(25, 25, 'S')
        num_steps = 500
        positions = [(individual.x, individual.y)]
        
        # RecordMoveAutotrajectory
        for _ in range(num_steps):
            individual.move(self.sigma, self.grid_size)
            positions.append((individual.x, individual.y))
        
        positions = np.array(positions)
        
        # DesignCalculateTotalPositionMove
        total_displacement = np.sqrt((positions[-1][0] - positions[0][0])**2 + 
                                   (positions[-1][1] - positions[0][1])**2)
        
        # DesignCalculateTotalPathLengthDegrees
        total_path_length = 0
        for i in range(1, len(positions)):
            step_length = np.sqrt((positions[i][0] - positions[i-1][0])**2 + 
                                (positions[i][1] - positions[i-1][1])**2)
            total_path_length += step_length
        
        # randomMachinewalkSpecialness:TotalPositionMoveShouldThisRemoteSmallAtTotalPathLengthDegrees
        efficiency = total_displacement / total_path_length
        assert efficiency < 0.3, \
            f"randomMachinewalkEffectRate{efficiency}OverHigh,ShouldThisSmallAt0.3(IntegratedImplementationrandomMachineness)"
        
        # VerifytrajectoryrandomMachineness:CameraadjacentStepstepOfficialDirectionShouldThisCameraforrandomMachine
        directions = []
        for i in range(1, len(positions)):
            dx = positions[i][0] - positions[i-1][0]
            dy = positions[i][1] - positions[i-1][1]
            if dx != 0 or dy != 0:  # excludeRemovenotHasMoveAutoSituationstate
                angle = np.arctan2(dy, dx)
                directions.append(angle)
        
        if len(directions) > 10:
            # OfficialDirectionMarkStandardDifferenceShouldThissufficientLarge(IntegratedImplementationrandomMachineness)
            direction_std = np.std(directions)
            assert direction_std > 1.0, \
                f"MoveAutoOfficialDirectionMarkStandardDifference{direction_std}OverSmall,ShouldThisIntegratedImplementationrandomMachineness"
        
        print("randomMachinewalkSpecialnessTest Passed")


if __name__ == "__main__":
    # RunTest
    test_instance = TestBrownianMotion()
    test_instance.setup_method()
    
    try:
        test_instance.test_brownian_motion_characteristics()
        test_instance.test_movement_distance_distribution()
        test_instance.test_motion_intensity_parameter_effect()
        test_instance.test_grid_boundary_constraints()
        test_instance.test_isolation_prevents_movement()
        test_instance.test_random_walk_properties()
        print("\nPlaceHasDistributionrandomSportsTest Passed!")
    except AssertionError as e:
        print(f"\nTest Failed: {e}")
    except Exception as e:
        print(f"\nTestOutputWrong: {e}")