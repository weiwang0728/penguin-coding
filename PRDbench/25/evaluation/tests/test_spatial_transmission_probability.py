# -*- coding: utf-8 -*-
"""
EmptyBetweenTraditionalSpreadSummaryRateDesignCalculateUnit Test
TestSpatialBrownianModelCategoryinEmptyBetweenTraditionalSpreadSummaryRateDesignCalculateFunction
"""

import pytest
import numpy as np
import os
import sys

# AddsrcDirectorytoPath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from models.spatial_brownian_model import SpatialBrownianModel, Individual


class TestSpatialTransmissionProbability:
    """EmptyBetweenTraditionalSpreadSummaryRateDesignCalculateTestCategory"""
    
    def setup_method(self):
        """eachitem(s)TestOfficialMethodbeforeDesignSet"""
        # CreateOneitem(s)SimpleSingleConfigureUseAtTest
        test_config = {
            'grid_size': 50,
            'num_individuals': 100,
            'sigma': 2,
            'transmission_distance': 4,  # TraditionalSpreadDistanceDistanceThresholdValueas4
            'beta': 0.04,               # TraditionalSpreadRate
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
        
    def test_transmission_probability_distance_correlation(self):
        """TestTraditionalSpreadSummaryRateandEmptyBetweenDistanceDistanceNegativeCameraRelatedRelatedSeries
        
        Verify:
        1. TraditionalSpreadSummaryRateandEmptyBetweenDistanceDistanceshowNegativeCameraRelated
        2. DistanceDistancemorenearTraditionalSpreadSummaryRatemoreHigh
        3. UltraOver4item(s)gridFormatSinglePositionTraditionalSpreadSummaryRateas0
        """
        
        # CreateOneitem(s)InfectionInfectionErinNativePoint
        infected = Individual(10, 10, 'I')
        
        # CreateManyitem(s)EasyInfectionErinNotSameDistanceDistance
        test_distances = [0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        transmission_probs = []
        
        for distance in test_distances:
            # CreateEasyInfectionErinIndicatorFixedDistanceDistance
            susceptible = Individual(10 + distance, 10, 'S')
            
            # VerifyImplementationInternationalDistanceDistance
            actual_distance = self.model.calculate_distance(infected, susceptible)
            assert abs(actual_distance - distance) < 1e-10, \
                f"DistanceDistanceDesignSetError:Periodexpected{distance},ImplementationInternational{actual_distance}"
            
            # DesignCalculateTraditionalSpreadSummaryRate(FoundationAtSourceGenerationCodeinOfficeStyle)
            if distance <= self.model.transmission_distance:
                # prob = beta * exp(-distance) * dt
                expected_prob = self.model.beta * np.exp(-distance) * self.model.dt
                transmission_probs.append(expected_prob)
            else:
                # UltraOverThresholdValue,SummaryRateas0
                expected_prob = 0.0
                transmission_probs.append(expected_prob)
            
            print(f"DistanceDistance{distance}: TraditionalSpreadSummaryRate{expected_prob:.6f}")
        
        # VerifyNegativeCameraRelatedRelatedSeries(inThresholdValueInternal)
        within_threshold_distances = [d for d in test_distances if d <= self.model.transmission_distance]
        within_threshold_probs = transmission_probs[:len(within_threshold_distances)]
        
        # CheckDistanceDistancemorenearSummaryRatemoreHigh(inThresholdValueInternal)
        for i in range(len(within_threshold_probs) - 1):
            assert within_threshold_probs[i] > within_threshold_probs[i + 1], \
                f"DistanceDistance{within_threshold_distances[i]}SummaryRateShouldThisLargeAtDistanceDistance{within_threshold_distances[i+1]}SummaryRate"
        
        # VerifyUltraOverThresholdValueSummaryRateas0
        beyond_threshold_probs = transmission_probs[len(within_threshold_distances):]
        for prob in beyond_threshold_probs:
            assert prob == 0.0, f"UltraOverTraditionalSpreadDistanceDistanceThresholdValueSummaryRateShouldas0,ImplementationInternationalas{prob}"
        
        print("TraditionalSpreadSummaryRateandDistanceDistanceNegativeCameraRelatedRelatedSeriesVerifyPass")
    
    def test_transmission_probability_formula(self):
        """TestTraditionalSpreadSummaryRateDesignCalculateOfficeStyleCorrectAccurateness"""
        
        # TestTraditionalSpreadSummaryRateOfficeStyle:prob = beta * exp(-distance) * dt
        beta = self.model.beta
        dt = self.model.dt
        
        test_cases = [
            (0.0, beta * np.exp(0) * dt),      # DistanceDistanceas0
            (1.0, beta * np.exp(-1) * dt),     # DistanceDistanceas1
            (2.0, beta * np.exp(-2) * dt),     # DistanceDistanceas2
            (3.0, beta * np.exp(-3) * dt),     # DistanceDistanceas3
            (4.0, beta * np.exp(-4) * dt),     # boundaryBoundarySituationstate:DistanceDistanceas4
            (5.0, 0.0),                        # UltraOverThresholdValue:DistanceDistanceas5
        ]
        
        for distance, expected_prob in test_cases:
            # Createitem(s)Integrated
            infected = Individual(0, 0, 'I')
            susceptible = Individual(distance, 0, 'S')
            
            # VerifyDistanceDistance
            actual_distance = self.model.calculate_distance(infected, susceptible)
            assert abs(actual_distance - distance) < 1e-10
            
            # VerifySummaryRateDesignCalculate
            if distance <= self.model.transmission_distance:
                calculated_prob = beta * np.exp(-distance) * dt
            else:
                calculated_prob = 0.0
            
            assert abs(calculated_prob - expected_prob) < 1e-10, \
                f"DistanceDistance{distance}TraditionalSpreadSummaryRateDesignCalculateError:Periodexpected{expected_prob},ImplementationInternational{calculated_prob}"
        
        print("TraditionalSpreadSummaryRateOfficeStyleVerifyPass")
    
    def test_transmission_probability_parameters_effect(self):
        """TestTraditionalSpreadSummaryRateParameterShadowResponse"""
        
        # TestNotSamebetaValueShadowResponse
        original_beta = self.model.beta
        distance = 2.0
        
        beta_values = [0.01, 0.02, 0.04, 0.08]
        
        for beta in beta_values:
            self.model.beta = beta
            expected_prob = beta * np.exp(-distance) * self.model.dt
            
            # VerifybetaValueandSummaryRateSuccessCorrectBifer
            if beta > original_beta:
                original_prob = original_beta * np.exp(-distance) * self.model.dt
                assert expected_prob > original_prob, \
                    f"UpdateLargebeta({beta})ShouldThisMadeNativeUpdateLargeTraditionalSpreadSummaryRate"
        
        # ResumeRecoveryNativeInitialbetaValue
        self.model.beta = original_beta
        
        # TestTimeBetweenStepLengthdtShadowResponse
        original_dt = self.model.dt
        dt_values = [0.5, 1.0, 2.0]
        
        for dt in dt_values:
            self.model.dt = dt
            expected_prob = self.model.beta * np.exp(-distance) * dt
            
            # VerifydtValueandSummaryRateSuccessCorrectBifer
            if dt > original_dt:
                original_prob = self.model.beta * np.exp(-distance) * original_dt
                assert expected_prob > original_prob, \
                    f"UpdateLargedt({dt})ShouldThisMadeNativeUpdateLargeTraditionalSpreadSummaryRate"
        
        # ResumeRecoveryNativeInitialdtValue
        self.model.dt = original_dt
        
        print("TraditionalSpreadSummaryRateParameterShadowResponseTest Passed")
    
    def test_transmission_distance_threshold_effect(self):
        """TestTraditionalSpreadDistanceDistanceThresholdValueShadowResponse"""
        
        # TestboundaryBoundarySituationstate
        threshold = self.model.transmission_distance  # 4.0
        
        # inThresholdValueInternal
        just_within = threshold - 0.1  # 3.9
        prob_within = self.model.beta * np.exp(-just_within) * self.model.dt
        assert prob_within > 0, f"ThresholdValueInternalDistanceDistance{just_within}TraditionalSpreadSummaryRateShouldLargeAt0"
        
        # inThresholdValueon
        exactly_at = threshold  # 4.0
        prob_at = self.model.beta * np.exp(-exactly_at) * self.model.dt
        assert prob_at > 0, f"ThresholdValueDistanceDistance{exactly_at}TraditionalSpreadSummaryRateShouldLargeAt0"
        
        # UltraOverThresholdValue
        just_beyond = threshold + 0.1  # 4.1
        prob_beyond = 0.0  # ShouldThisas0
        assert prob_beyond == 0, f"UltraOverThresholdValueDistanceDistance{just_beyond}TraditionalSpreadSummaryRateShouldas0"
        
        print("TraditionalSpreadDistanceDistanceThresholdValueEffectResultTest Passed")
    
    def test_exponential_decay_property(self):
        """TestIndicatorNumberdecaySpecialness"""
        
        # CreateDistanceDistanceSequenceSeries
        distances = np.linspace(0.1, 3.9, 20)  # inThresholdValueInternalDistanceDistance
        probabilities = []
        
        for distance in distances:
            prob = self.model.beta * np.exp(-distance) * self.model.dt
            probabilities.append(prob)
        
        probabilities = np.array(probabilities)
        
        # VerifyIndicatorNumberdecaySpecialness
        # 1. SummaryRateShouldThisrandomDistanceDistanceSingleAdjustdecrease
        for i in range(len(probabilities) - 1):
            assert probabilities[i] > probabilities[i + 1], \
                f"SummaryRateShouldThisrandomDistanceDistanceSingleAdjustdecrease,butinPositionSet{i}ProcessorSendImplementationincreaseIncrease"
        
        # 2. DesignCalculatedecayRate,ShouldThisInterfacenearIndicatorNumberdecay
        log_probs = np.log(probabilities)
        # LinenessReturnregression slopeRateShouldThisapproximatelyas-1(IndicatorNumberdecaySpecialfeature)
        slope = np.polyfit(distances, log_probs, 1)[0]
        
        assert abs(slope + 1.0) < 0.1, \
            f"IndicatorNumberdecayslopeRateShouldInterfacenear-1,ImplementationInternationalas{slope}"
        
        print("IndicatorNumberdecaySpecialnessVerifyPass")
    
    def test_probability_bounds(self):
        """TestSummaryRateboundaryBoundaryValue"""
        
        # TestSummaryRateValueCombineProcessorness
        distances = [0.5, 1.0, 2.0, 3.0, 4.0]
        
        for distance in distances:
            if distance <= self.model.transmission_distance:
                prob = self.model.beta * np.exp(-distance) * self.model.dt
                
                # SummaryRateShouldThisin[0, 1]RangerangeInternal
                assert 0 <= prob <= 1, \
                    f"SummaryRate{prob}UltraOutput[0,1]Rangerange,DistanceDistance={distance}"
                
                # forAtCombineProcessorParameter,SummaryRateNotShouldThisOverLarge
                assert prob <= 0.5, \
                    f"SingleStepTraditionalSpreadSummaryRate{prob}OverLarge,DistanceDistance={distance}"
            else:
                prob = 0.0
                assert prob == 0.0, \
                    f"UltraOverThresholdValueSummaryRateShouldas0,DistanceDistance={distance}"
        
        print("SummaryRateboundaryBoundaryValueTest Passed")
    
    def test_transmission_step_probability_application(self):
        """TestTraditionalSpreadStepstepinSummaryRateImplementationInternationalShouldUse"""
        
        # CreateSimpleSingleTestscenario
        self.model.individuals = [
            Individual(10, 10, 'I'),  # InfectionInfectionEr
            Individual(11, 10, 'S'),  # EasyInfectionEr,DistanceDistance=1
            Individual(15, 10, 'S')   # EasyInfectionEr,DistanceDistance=5(UltraOverThresholdValue)
        ]
        
        # DesignSetHighTraditionalSpreadRatetoPortableViewObserveEffectResult
        self.model.beta = 1.0
        
        # ManyTimesExecuteTraditionalSpreadStepstep,SystemDesignTraditionalSpreadSituationstate
        transmissions_close = 0
        transmissions_far = 0
        num_trials = 1000
        
        for _ in range(num_trials):
            # WeightSetEasyInfectionErStatus
            self.model.individuals[1].state = 'S'
            self.model.individuals[2].state = 'S'
            
            # ExecuteTraditionalSpreadStepstep
            self.model.transmission_step()
            
            # CheckTraditionalSpreadResult
            if self.model.individuals[1].state == 'E':
                transmissions_close += 1
            if self.model.individuals[2].state == 'E':
                transmissions_far += 1
        
        # VerifyTraditionalSpreadSummaryRateImplementationInternationalShouldUse
        # nearDistanceDistanceitem(s)IntegratedShouldThisHasTraditionalSpreadSendNative
        close_transmission_rate = transmissions_close / num_trials
        assert close_transmission_rate > 0, "nearDistanceDistanceitem(s)IntegratedShouldThisSendNativeTraditionalSpread"
        
        # RemoteDistanceDistanceitem(s)Integrated(UltraOverThresholdValue)NotShouldThisHasTraditionalSpread
        far_transmission_rate = transmissions_far / num_trials
        assert far_transmission_rate == 0, f"UltraOverThresholdValueitem(s)IntegratedNotShouldThisbeTraditionalSpread,butSendNative{transmissions_far}Times"
        
        print("TraditionalSpreadStepstepSummaryRateShouldUseTest Passed")


if __name__ == "__main__":
    # RunTest
    test_instance = TestSpatialTransmissionProbability()
    test_instance.setup_method()
    
    try:
        test_instance.test_transmission_probability_distance_correlation()
        test_instance.test_transmission_probability_formula()
        test_instance.test_transmission_probability_parameters_effect()
        test_instance.test_transmission_distance_threshold_effect()
        test_instance.test_exponential_decay_property()
        test_instance.test_probability_bounds()
        test_instance.test_transmission_step_probability_application()
        print("\nPlaceHasEmptyBetweenTraditionalSpreadSummaryRateDesignCalculateTest Passed!")
    except AssertionError as e:
        print(f"\nTest Failed: {e}")
    except Exception as e:
        print(f"\nTestOutputWrong: {e}")