# -*- coding: utf-8 -*-
"""
IsolationDistanceEffectResultNumberValueVerifyUnit Test
TestIsolationDistanceMachineControlforInfectionInfectionTraditionalSpreadNumberValueShadowResponse
"""

import pytest
import numpy as np
import os
import sys

# AddsrcDirectorytoPath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from models.isolation_seir_model import IsolationSEIRModel


class TestIsolationEffectiveness:
    """IsolationDistanceEffectResultNumberValueVerifyTestCategory"""
    
    def setup_method(self):
        """eachitem(s)TestOfficialMethodbeforeDesignSet"""
        # FoundationStandardConfigure(NoIsolationDistance)
        self.base_config = {
            'N': 10000,
            'beta': 0.3,                 # IncreasePlusTraditionalSpreadRateUseepidemicSituationEnergyenoughTraditionalSpread
            'sigma': 0.2,                # IncreasePlusLatentlatentPeriodConversionRate
            'gamma': 0.1,
            'q': 0.0,                    # NoIsolationDistance
            'deltaI': 0.0,
            'gammaI': 0.0,
            'lambda_val': 0.0,
            'deltaH': 0.0,
            'alpha': 0.0,
            'S0': 9990,                  # decreaseless_thanInitialInitialEasyInfectionEr,IncreasePlusInitialInitialInfectionInfectionEr
            'E0': 5,                     # IncreasePlusInitialInitialLatentlatentEr
            'I0': 5,                     # IncreasePlusInitialInitialInfectionInfectionEr
            'Sq0': 0,
            'Eq0': 0,
            'H0': 0,
            'R0': 0,
            'days': 100,                 # IncreasePlusModelSimulationDayNumber
            'dt': 1
        }
        
        # IsolationDistanceConfigure
        self.isolation_config = self.base_config.copy()
        self.isolation_config.update({
            'q': 0.01,                   # IncreasePlusIsolationDistanceRate
            'deltaI': 0.13,              # hospitalizationRate
            'gammaI': 0.007,             # hospitalizationHealthRecoveryRate
            'lambda_val': 0.03,          # IsolationDistanceTraditionalSpreadRate
            'deltaH': 0.008,             # OutputhospitalRate
            'alpha': 0.0001              # deathRate
        })
        
    def test_isolation_reduces_infection_peak(self):
        """TestIsolationDistancemeasures significantlyDecreaseLowInfectionInfectionPeakValue
        
        Verify:
        1. IsolationDistancemeasures significantlyDecreaseLowInfectionInfectionPeakValue(CameraBiferNoIsolationDistanceSituationstateDecreaseLow≥30%)
        2. IsolationDistancePersongroupQuantityCombineProcessorIncreaseLength
        """
        
        # RunNoIsolationDistanceModelType
        base_model = IsolationSEIRModel(self.base_config)
        base_model.solve_ode()
        
        # RunIsolationDistanceModelType
        isolation_model = IsolationSEIRModel(self.isolation_config)
        isolation_model.solve_ode()
        
        # DesignCalculateInfectionInfectionPeakValue
        base_peak = np.max(base_model.I)
        isolation_peak = np.max(isolation_model.I)
        
        # DesignCalculatePeakValueDecreaseLowRate
        reduction_rate = (base_peak - isolation_peak) / base_peak
        
        print(f"NoIsolationDistanceInfectionInfectionPeakValue: {base_peak:.0f}")
        print(f"IsolationDistanceInfectionInfectionPeakValue: {isolation_peak:.0f}")
        print(f"PeakValueDecreaseLowRate: {reduction_rate:.1%}")
        
        # VerifyIsolationDistancemeasures significantlyDecreaseLowInfectionInfectionPeakValue(≥30%)
        assert reduction_rate >= 0.30, \
            f"IsolationDistancemeasureShouldDecreaseLowInfectionInfectionPeakValue≥30%,ImplementationInternationalDecreaseLow{reduction_rate:.1%}"
        
        # VerifyIsolationDistancePersongroupQuantityCombineProcessorIncreaseLength
        max_hospitalized = np.max(isolation_model.H)
        max_isolated_susceptible = np.max(isolation_model.Sq)
        max_isolated_exposed = np.max(isolation_model.Eq)
        
        total_isolated = max_hospitalized + max_isolated_susceptible + max_isolated_exposed
        
        # IsolationDistancePersongroupShouldThisaccount_forTotalPersonPortCombineProcessorBiferExample
        isolation_rate = total_isolated / self.isolation_config['N']
        assert 0.001 <= isolation_rate <= 0.8, \
            f"IsolationDistancePersongroupBiferExample{isolation_rate:.1%}NotinCombineProcessorRangerange[0.1%, 80%]Internal"
        
        print(f"MostLargehospitalizationPersonNumber: {max_hospitalized:.0f}")
        print(f"MostLargeIsolationDistanceEasyInfectionEr: {max_isolated_susceptible:.0f}")
        print(f"MostLargeIsolationDistanceLatentlatentEr: {max_isolated_exposed:.0f}")
        print(f"TotalIsolationDistancePersongroupBiferExample: {isolation_rate:.1%}")
        
        print("IsolationDistanceEffectResultNumberValueVerifyTest Passed")
    
    def test_isolation_delays_epidemic_progression(self):
        """TestIsolationDistancemeasures delay epidemicSituationSendextension"""
        
        # Runtwoitem(s)ModelType
        base_model = IsolationSEIRModel(self.base_config)
        base_model.solve_ode()
        
        isolation_model = IsolationSEIRModel(self.isolation_config)
        isolation_model.solve_ode()
        
        # findtoInfectionInfectionPeakValueOutputImplementationTimeBetween
        base_peak_time = np.argmax(base_model.I)
        isolation_peak_time = np.argmax(isolation_model.I)
        
        print(f"NoIsolationDistancePeakValueTimeBetween: index{base_peak_time}Day")
        print(f"IsolationDistancePeakValueTimeBetween: index{isolation_peak_time}Day")
        
        # IsolationDistanceShouldThisdelayepidemicSituationHighPeak
        time_delay = isolation_peak_time - base_peak_time
        assert time_delay >= 0, \
            f"IsolationDistancemeasureShoulddelayepidemicSituationHighPeak,butExtractbefore{-time_delay}Day"
        
        print(f"epidemicSituationHighPeakdelay: {time_delay}Day")
        
        # VerifyMostEndcumulativeInfectionInfectionRateDecreaseLow
        base_final_attack_rate = (self.base_config['N'] - base_model.S[-1]) / self.base_config['N']
        isolation_final_attack_rate = (self.isolation_config['N'] - isolation_model.S[-1]) / self.isolation_config['N']
        
        attack_rate_reduction = base_final_attack_rate - isolation_final_attack_rate
        
        print(f"NoIsolationDistanceMostEndattackRate: {base_final_attack_rate:.1%}")
        print(f"IsolationDistanceMostEndattackRate: {isolation_final_attack_rate:.1%}")
        print(f"attackRateDecreaseLow: {attack_rate_reduction:.1%}")
        
        assert attack_rate_reduction >= 0, \
            "IsolationDistancemeasureShouldThisDecreaseLowMostEndattackRate"
        
        print("epidemicSituationSendextend and delayTest Passed")
    
    def test_isolation_compartments_dynamics(self):
        """TestIsolationDistancecabinRoomAutostateChangeization"""
        
        isolation_model = IsolationSEIRModel(self.isolation_config)
        isolation_model.solve_ode()
        
        # VerifyIsolationDistancecabinRoomCombineProcessorness
        # 1. IsolationDistanceEasyInfectionErQuantity
        Sq = isolation_model.Sq
        assert np.all(Sq >= 0), "IsolationDistanceEasyInfectionErQuantityNotEnergyasNegative"
        assert np.max(Sq) > 0, "IsolationDistanceEasyInfectionErQuantityShouldThisHasIncreaseLength"
        
        # 2. IsolationDistanceLatentlatentErQuantity
        Eq = isolation_model.Eq
        assert np.all(Eq >= 0), "IsolationDistanceLatentlatentErQuantityNotEnergyasNegative"
        
        # 3. hospitalizationErQuantity
        H = isolation_model.H
        assert np.all(H >= 0), "hospitalizationErQuantityNotEnergyasNegative"
        assert np.max(H) > 0, "hospitalizationErQuantityShouldThisHasIncreaseLength"
        
        # 4. VerifycabinRoomTotalandconservation
        total_population = isolation_model.S + isolation_model.Sq + isolation_model.E + isolation_model.Eq + isolation_model.I + isolation_model.H + isolation_model.R
        expected_total = self.isolation_config['N']
        
        for t in range(len(total_population)):
            assert abs(total_population[t] - expected_total) < 1e-6, \
                f"index{t}DayPersonPortTotalNumberNotconservation: {total_population[t]} ≠ {expected_total}"
        
        print("IsolationDistancecabinRoomAutostateChangeizationTest Passed")
    
    def test_isolation_parameters_sensitivity(self):
        """TestIsolationDistanceParametersensitivityInfectionness"""
        
        # TestNotSameIsolationDistanceRateShadowResponse
        isolation_rates = [0.0, 0.000001, 0.00001, 0.0001]
        peak_infections = []
        
        for q in isolation_rates:
            config = self.base_config.copy()
            config.update({
                'q': q,
                'deltaI': 0.13,
                'gammaI': 0.007,
                'lambda_val': 0.03,
                'deltaH': 0.008,
                'alpha': 0.0001
            })
            
            model = IsolationSEIRModel(config)
            model.solve_ode()
            peak_infections.append(np.max(model.I))
        
        # VerifyIsolationDistanceRatemoreHigh,InfectionInfectionPeakValuemoreLow
        for i in range(len(isolation_rates) - 1):
            if isolation_rates[i+1] > isolation_rates[i]:
                assert peak_infections[i+1] <= peak_infections[i], \
                    f"UpdateHighIsolationDistanceRateShouldThisleadCauseUpdateLowInfectionInfectionPeakValue"
        
        print("IsolationDistanceParametersensitivityInfectionnessTest Passed")
    
    def test_isolation_effectiveness_metrics(self):
        """TestIsolationDistanceEffectResultEditionizationIndicatorMark"""
        
        # RunFoundationStandardandIsolationDistanceModelType
        base_model = IsolationSEIRModel(self.base_config)
        base_model.solve_ode()
        
        isolation_model = IsolationSEIRModel(self.isolation_config)
        isolation_model.solve_ode()
        
        # DesignCalculateManyitem(s)EffectResultIndicatorMark
        metrics = {}
        
        # 1. PeakValueDecreaseLowRate
        base_peak = np.max(base_model.I)
        isolation_peak = np.max(isolation_model.I)
        metrics['peak_reduction'] = (base_peak - isolation_peak) / base_peak
        
        # 2. MostEndattackRateDecreaseLow
        base_attack_rate = (self.base_config['N'] - base_model.S[-1]) / self.base_config['N']
        isolation_attack_rate = (self.isolation_config['N'] - isolation_model.S[-1]) / self.isolation_config['N']
        metrics['attack_rate_reduction'] = base_attack_rate - isolation_attack_rate
        
        # 3. epidemicSituationSupportContinueTimeBetweenChangeization
        # FixedDefinitionepidemicSituationResultBundleasInfectionInfectionErQuantityLowAtInitialInitialValue
        base_duration = len(base_model.I)
        isolation_duration = len(isolation_model.I)
        metrics['duration_change'] = isolation_duration - base_duration
        
        # 4. cumulativeInfectionInfectionPersonNumberDecreaseLow
        base_cumulative = np.sum(np.diff(np.concatenate([[0], base_model.R])))
        isolation_cumulative = np.sum(np.diff(np.concatenate([[0], isolation_model.R])))
        metrics['cumulative_reduction'] = (base_cumulative - isolation_cumulative) / base_cumulative
        
        # VerifyIndicatorMarkCombineProcessorness
        assert metrics['peak_reduction'] >= 0.30, \
            f"PeakValueDecreaseLowRate{metrics['peak_reduction']:.1%}Should≥30%"
        
        assert metrics['attack_rate_reduction'] >= 0, \
            f"attackRateShouldThisDecreaseLow,ImplementationInternationalChangeization{metrics['attack_rate_reduction']:.1%}"
        
        print(f"IsolationDistanceEffectResultIndicatorMark:")
        print(f"  PeakValueDecreaseLowRate: {metrics['peak_reduction']:.1%}")
        print(f"  attackRateDecreaseLow: {metrics['attack_rate_reduction']:.1%}")
        print(f"  SupportContinueTimeBetweenChangeization: {metrics['duration_change']}Day")
        print(f"  cumulativeInfectionInfectionDecreaseLow: {metrics['cumulative_reduction']:.1%}")
        
        print("IsolationDistanceEffectResultEditionizationIndicatorMarkTest Passed")
    
    def test_isolation_cost_benefit_analysis(self):
        """TestIsolationDistancemeasureSuccessBookEffectbenefitAnalysis"""
        
        isolation_model = IsolationSEIRModel(self.isolation_config)
        isolation_model.solve_ode()
        
        # DesignCalculateIsolationDistance"SuccessBook"(IsolationDistancePersonNumber)
        total_isolated_person_days = (
            np.sum(isolation_model.Sq) +  # IsolationDistanceEasyInfectionErPersonDay
            np.sum(isolation_model.Eq) +  # IsolationDistanceLatentlatentErPersonDay
            np.sum(isolation_model.H)     # hospitalizationErPersonDay
        )
        
        # DesignCalculateIsolationDistance"Receivebenefit"(avoidInfectionInfection)
        base_model = IsolationSEIRModel(self.base_config)
        base_model.solve_ode()
        
        base_final_infected = self.base_config['N'] - base_model.S[-1]
        isolation_final_infected = self.isolation_config['N'] - isolation_model.S[-1]
        infections_prevented = base_final_infected - isolation_final_infected
        
        # DesignCalculateEffectbenefitBifer
        if total_isolated_person_days > 0:
            cost_effectiveness = infections_prevented / (total_isolated_person_days / len(isolation_model.S))
            
            # SuccessBookEffectbenefitShouldThisCombineProcessor(eachIsolationDistanceOneitem(s)PersonDayShouldThisEnergyexpectedpreventCombineProcessorQuantityInfectionInfection)
            assert cost_effectiveness > 0, "IsolationDistancemeasureShouldThisHasCorrectSurfaceEffectbenefit"
            
            print(f"IsolationDistancePersonDayNumber: {total_isolated_person_days:.0f}")
            print(f"expectedpreventInfectionInfectionNumber: {infections_prevented:.0f}")
            print(f"SuccessBookEffectbenefitBifer: {cost_effectiveness:.3f}")
        
        print("IsolationDistanceSuccessBookEffectbenefitAnalysisTest Passed")


if __name__ == "__main__":
    # RunTest
    test_instance = TestIsolationEffectiveness()
    test_instance.setup_method()
    
    try:
        test_instance.test_isolation_reduces_infection_peak()
        test_instance.test_isolation_delays_epidemic_progression()
        test_instance.test_isolation_compartments_dynamics()
        test_instance.test_isolation_parameters_sensitivity()
        test_instance.test_isolation_effectiveness_metrics()
        test_instance.test_isolation_cost_benefit_analysis()
        print("\nPlaceHasIsolationDistanceEffectResultNumberValueVerifyTest Passed!")
    except AssertionError as e:
        print(f"\nTest Failed: {e}")
    except Exception as e:
        print(f"\nTestOutputWrong: {e}")