import unittest
import sys
import os
import numpy as np

# AddsrcDirectorytoPythonPath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from models.sir_model import SIRModel


class TestSIRModelAlgorithm(unittest.TestCase):
    """SIRModelTypeCoreCoreCalculateMethodTestCategory"""
    
    def setUp(self):
        """TestbeforeStandardPrepare"""
        self.N = 10000  # TotalPersonPortNumber
        self.beta = 0.05  # TraditionalSpreadRate
        self.gamma = 0.1  # HealthRecoveryRate
        self.days = 100  # ModelSimulationDayNumber
        
    def test_sir_model_core_algorithm(self):
        """TestSIRModelTypeCoreCoreCalculateMethodImplementationImplementation"""
        # CreateAutoFixedDefinitionConfigure
        config = {
            'N': self.N,
            'beta': self.beta,
            'gamma': self.gamma,
            'S0': self.N - 1,
            'I0': 1,
            'R0': 0,
            'days': self.days,
            'dt': 1
        }
        
        # CreateSIRModelTypeImplementationExample
        model = SIRModel(config=config)
        
        # RunModelSimulation
        results = model.run_simulation()
        S = results['S']
        I = results['I']
        R = results['R']
        
        # Test1: VerifyArrayLengthDegrees
        self.assertEqual(len(S), self.days + 1, "SSequenceSeriesLengthDegreesShouldasdays+1")
        self.assertEqual(len(I), self.days + 1, "ISequenceSeriesLengthDegreesShouldasdays+1")
        self.assertEqual(len(R), self.days + 1, "RSequenceSeriesLengthDegreesShouldasdays+1")
        
        # Test2: VerifyInitialInitialentryPiece
        self.assertEqual(S[0], self.N - 1, f"InitialInitialEasyInfectionErQuantityShouldas{self.N-1}")
        self.assertEqual(I[0], 1, "InitialInitialInfectionInfectionErQuantityShouldas1")
        self.assertEqual(R[0], 0, "InitialInitialHealthRecoveryErQuantityShouldas0")
        
        # Test3: VerifyconservationFixedlaw S(t) + I(t) + R(t) = N
        for t in range(len(S)):
            total = S[t] + I[t] + R[t]
            self.assertAlmostEqual(total, self.N, places=6, 
                                 msg=f"TimeBetweenPoint{t}conservationFixedlawFailEffect: S({t})={S[t]}, I({t})={I[t]}, R({t})={R[t]}, Totaland={total}")
        
        # Test4: VerifySingleAdjustness
        # S(t)ShouldSingleAdjustdecrease
        for t in range(1, len(S)):
            self.assertLessEqual(S[t], S[t-1], f"S(t)int={t}TimeviolateReverseSingleAdjustdecreaseness")
        
        # R(t)ShouldSingleAdjustincreaseIncrease
        for t in range(1, len(R)):
            self.assertGreaterEqual(R[t], R[t-1], f"R(t)int={t}TimeviolateReverseSingleAdjustincreaseIncreaseness")
        
        # I(t)ShouldfirstIncreaseafterdecrease(SaveinPeakValue)
        # forAtR0 < 1Situationstate,I(t)CanEnergySingleAdjustdecrease,PlacetothisinsideVerifyI(t)MostEndapproachAt0
        self.assertLess(I[-1], I[0], "I(t)MostEndShouldSmallAtInitialInitialValue")
        
        # Test5: VerifyR0DesignCalculateandShadowResponse
        R0 = self.beta / self.gamma
        self.assertAlmostEqual(R0, 0.5, places=6, msg="R0DesignCalculateError")
        
        # becauseAtR0 < 1,epidemicSituationNotShouldLargeRuleModeloutbreakSend
        max_infected = max(I)
        self.assertLess(max_infected, self.N * 0.1, 
                       f"R0<1TimeInfectionInfectionPeakValue{max_infected}NotShouldUltraOverPersonPort10%")
        
        # Test6: VerifyMostEndStatus
        final_S = S[-1]
        final_I = I[-1]
        final_R = R[-1]
        
        # MostEndInfectionInfectionErShouldInterfacenear0
        self.assertLess(final_I, 1, "MostEndInfectionInfectionErQuantityShouldInterfacenear0")
        
        # MostEndEasyInfectionErShouldLargeAt0(CauseasR0<1)
        self.assertGreater(final_S, self.N * 0.9, 
                          f"R0<1TimeMostEndEasyInfectionEr{final_S}ShouldLargeAtPersonPort90%")
        
        # Test7: VerifyNumberValuestableFixedness(NoNaNorInf)
        self.assertTrue(np.all(np.isfinite(S)), "SSequenceSeriesContainsnonHasLimitedNumberValue")
        self.assertTrue(np.all(np.isfinite(I)), "ISequenceSeriesContainsnonHasLimitedNumberValue")
        self.assertTrue(np.all(np.isfinite(R)), "RSequenceSeriesContainsnonHasLimitedNumberValue")
        
        # Test8: VerifynonNegativeness
        self.assertTrue(np.all(S >= 0), "SSequenceSeriesContainsNegativeNumber")
        self.assertTrue(np.all(I >= 0), "ISequenceSeriesContainsNegativeNumber")
        self.assertTrue(np.all(R >= 0), "RSequenceSeriesContainsNegativeNumber")
        
        # Test9: VerifyHighR0SituationstateforBifer
        # RunHighTraditionalSpreadRateforBiferModelSimulation(R0 > 1)
        config_high = {
            'N': self.N,
            'beta': 0.3,
            'gamma': 0.1,
            'S0': self.N - 1,
            'I0': 1,
            'R0': 0,
            'days': self.days,
            'dt': 1
        }
        model_high = SIRModel(config=config_high)
        results_high = model_high.run_simulation()
        S_high = results_high['S']
        I_high = results_high['I']
        R_high = results_high['R']
        
        R0_high = 0.3 / 0.1  # R0 = 3.0 > 1
        
        # HighR0ShouldleadCauseUpdateLargeepidemicSituationoutbreakSend
        max_infected_high = max(I_high)
        self.assertGreater(max_infected_high, max_infected, 
                          "HighR0ModelTypeShouldHasUpdateLargeInfectionInfectionPeakValue")
        
        final_R_high = R_high[-1]
        self.assertGreater(final_R_high, final_R, 
                          "HighR0ModelTypeMostEndHealthRecoveryErShouldUpdateMany")
    
    def test_sir_model_parameter_validation(self):
        """TestSIRModelTypeParameterVerify"""
        # TestHasEffectParameter(WhenbeforeSIRModelImplementationImplementationCanEnergynotHasstrictFormatParameterVerify,PlacetofirstVerifyEnergyCorrectAccurateInitialInitialization)
        config = {
            'N': self.N,
            'beta': self.beta,
            'gamma': self.gamma,
            'S0': self.N - 1,
            'I0': 1,
            'R0': 0,
            'days': self.days,
            'dt': 1
        }
        model = SIRModel(config=config)
        self.assertIsNotNone(model)
    
    def test_sir_model_edge_cases(self):
        """TestSIRModelTypeboundaryBoundarySituationstate"""
        # TestUltraSmallPersonPort
        config_small = {
            'N': 3,
            'beta': 0.5,
            'gamma': 0.2,
            'S0': 2,
            'I0': 1,
            'R0': 0,
            'days': 20,
            'dt': 1
        }
        model_small = SIRModel(config=config_small)
        results_small = model_small.run_simulation()
        S_small = results_small['S']
        I_small = results_small['I']
        R_small = results_small['R']
        
        # VerifySmallRuleModelModelSimulationFoundationBooknessQuality
        self.assertEqual(S_small[0] + I_small[0] + R_small[0], 3)
        self.assertAlmostEqual(S_small[-1] + I_small[-1] + R_small[-1], 3, places=1)
        
        # TestzeroTraditionalSpreadRate
        config_zero = {
            'N': 100,
            'beta': 0.0,
            'gamma': 0.1,
            'S0': 99,
            'I0': 1,
            'R0': 0,
            'days': 50,
            'dt': 1
        }
        model_zero = SIRModel(config=config_zero)
        results_zero = model_zero.run_simulation()
        S_zero = results_zero['S']
        I_zero = results_zero['I']
        R_zero = results_zero['R']
        
        # zeroTraditionalSpreadRateTimeonlyHasHealthRecoveryOverProcess
        self.assertAlmostEqual(S_zero[-1], 99, places=1, msg="zeroTraditionalSpreadRateTimeEasyInfectionErQuantityShouldProtectionSupportNotChange")
        self.assertLess(I_zero[-1], 0.1, msg="zeroTraditionalSpreadRateTimeInfectionInfectionErMostEndShouldInterfacenear0")
        self.assertAlmostEqual(R_zero[-1], 1, places=1, msg="zeroTraditionalSpreadRateTimeonlyHasInitialInitialInfectionInfectionErHealthRecovery")
        
        # TestzeroHealthRecoveryRate(degradeizationasSIModelType)
        config_no_recovery = {
            'N': 100,
            'beta': 0.05,
            'gamma': 0.0,
            'S0': 99,
            'I0': 1,
            'R0': 0,
            'days': 200,
            'dt': 1
        }
        model_no_recovery = SIRModel(config=config_no_recovery)
        results_no_recovery = model_no_recovery.run_simulation()
        S_no_recovery = results_no_recovery['S']
        I_no_recovery = results_no_recovery['I']
        R_no_recovery = results_no_recovery['R']
        
        # zeroHealthRecoveryRateTimeHealthRecoveryErShouldInitialEndas0
        self.assertTrue(np.all(R_no_recovery < 0.1), "zeroHealthRecoveryRateTimeHealthRecoveryErShouldInterfacenear0")
        # ShoulddegradeizationasSIModelTypeLineas
        self.assertAlmostEqual(S_no_recovery[-1] + I_no_recovery[-1], 100, places=1)


if __name__ == '__main__':
    unittest.main()