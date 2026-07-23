import unittest
import sys
import os
import numpy as np

# AddsrcDirectorytoPythonPath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from models.si_model import SIModel


class TestSIModelAlgorithm(unittest.TestCase):
    """SIModelTypeCoreCoreCalculateMethodTestCategory"""
    
    def setUp(self):
        """TestbeforeStandardPrepare"""
        self.N = 10000  # TotalPersonPortNumber
        self.beta = 0.01  # TraditionalSpreadRate
        self.r = 10  # InterfaceTouchRate
        self.days = 200  # ModelSimulationDayNumber
        
    def test_si_model_core_algorithm(self):
        """TestSIModelTypeCoreCoreCalculateMethodImplementationImplementation"""
        # CreateAutoFixedDefinitionConfigure
        config = {
            'N': self.N,
            'beta': self.beta,
            'r': self.r,
            'S0': self.N - 1,
            'I0': 1,
            'days': self.days,
            'dt': 1
        }
        
        # CreateSIModelTypeImplementationExample
        model = SIModel(config=config)
        
        # RunModelSimulation
        results = model.run_simulation()
        S = results['S']
        I = results['I']
        
        # Test1: VerifyArrayLengthDegrees
        self.assertEqual(len(S), self.days + 1, "SSequenceSeriesLengthDegreesShouldasdays+1")
        self.assertEqual(len(I), self.days + 1, "ISequenceSeriesLengthDegreesShouldasdays+1")
        
        # Test2: VerifyInitialInitialentryPiece
        self.assertEqual(S[0], self.N - 1, f"InitialInitialEasyInfectionErQuantityShouldas{self.N-1}")
        self.assertEqual(I[0], 1, "InitialInitialInfectionInfectionErQuantityShouldas1")
        
        # Test3: VerifyconservationFixedlaw S(t) + I(t) = N
        for t in range(len(S)):
            total = S[t] + I[t]
            self.assertAlmostEqual(total, self.N, places=6, 
                                 msg=f"TimeBetweenPoint{t}conservationFixedlawFailEffect: S({t})={S[t]}, I({t})={I[t]}, Totaland={total}")
        
        # Test4: VerifySingleAdjustness
        # S(t)ShouldSingleAdjustdecrease
        for t in range(1, len(S)):
            self.assertLessEqual(S[t], S[t-1], f"S(t)int={t}TimeviolateReverseSingleAdjustdecreaseness")
        
        # I(t)ShouldSingleAdjustincreaseIncrease
        for t in range(1, len(I)):
            self.assertGreaterEqual(I[t], I[t-1], f"I(t)int={t}TimeviolateReverseSingleAdjustincreaseIncreaseness")
        
        # Test5: VerifyMostEndStatus
        final_S = S[-1]
        final_I = I[-1]
        
        # forAtSIModelType,MostEndPlaceHasPersonallwill beInfectionInfection(inHasLimitedTimeBetweenInternalCanEnergyNotCompleteAutomaticReceiveconverge)
        self.assertLess(final_S, self.N * 0.01, msg="MostEndEasyInfectionErQuantityShouldSmallAtTotalPersonPort1%")
        self.assertGreater(final_I, self.N * 0.99, msg=f"MostEndInfectionInfectionErQuantityShouldLargeAtTotalPersonPort99%")
        
        # Test6: VerifyNumberValuestableFixedness(NoNaNorInf)
        self.assertTrue(np.all(np.isfinite(S)), "SSequenceSeriesContainsnonHasLimitedNumberValue")
        self.assertTrue(np.all(np.isfinite(I)), "ISequenceSeriesContainsnonHasLimitedNumberValue")
        
        # Test7: VerifynonNegativeness
        self.assertTrue(np.all(S >= 0), "SSequenceSeriesContainsNegativeNumber")
        self.assertTrue(np.all(I >= 0), "ISequenceSeriesContainsNegativeNumber")
        
        # Test8: VerifyTraditionalSpreadRateShadowResponse
        # RunHighTraditionalSpreadRateforBiferModelSimulation
        config_high = {
            'N': self.N,
            'beta': self.beta * 2,
            'r': self.r,
            'S0': self.N - 1,
            'I0': 1,
            'days': self.days,
            'dt': 1
        }
        model_high = SIModel(config=config_high)
        results_high = model_high.run_simulation()
        S_high = results_high['S']
        I_high = results_high['I']
        
        # HighTraditionalSpreadRateShouldleadCauseUpdatefastInfectionInfectionTraditionalSpread
        mid_point = self.days // 2
        self.assertLess(S_high[mid_point], S[mid_point], 
                       "HighTraditionalSpreadRateModelTypeininPeriodShouldHasUpdateless_thanEasyInfectionEr")
        self.assertGreater(I_high[mid_point], I[mid_point], 
                          "HighTraditionalSpreadRateModelTypeininPeriodShouldHasUpdateManyInfectionInfectionEr")
    
    def test_si_model_parameter_validation(self):
        """TestSIModelTypeParameterVerify"""
        # TestNoEffectParameter(Noteintentional:WhenbeforeSIModelImplementationImplementationCanEnergynotHasParameterVerify,PlacetofirstSkipthisitem(s)Test)
        # thisinsideSimpleSingleVerifyModelTypeEnergyCorrectAccurateInitialInitialization
        config = {
            'N': self.N,
            'beta': self.beta,
            'r': self.r,
            'S0': self.N - 1,
            'I0': 1,
            'days': self.days,
            'dt': 1
        }
        model = SIModel(config=config)
        self.assertIsNotNone(model)
    
    def test_si_model_edge_cases(self):
        """TestSIModelTypeboundaryBoundarySituationstate"""
        # TestUltraSmallPersonPort
        config_small = {
            'N': 2,
            'beta': 0.5,
            'r': 1,
            'S0': 1,
            'I0': 1,
            'days': 10,
            'dt': 1
        }
        model_small = SIModel(config=config_small)
        results_small = model_small.run_simulation()
        S_small = results_small['S']
        I_small = results_small['I']
        
        # VerifySmallRuleModelModelSimulationFoundationBooknessQuality
        self.assertEqual(S_small[0] + I_small[0], 2)
        self.assertAlmostEqual(S_small[-1] + I_small[-1], 2, places=1)
        
        # TestzeroTraditionalSpreadRate
        config_zero = {
            'N': 100,
            'beta': 0.0,
            'r': self.r,
            'S0': 99,
            'I0': 1,
            'days': 50,
            'dt': 1
        }
        model_zero = SIModel(config=config_zero)
        results_zero = model_zero.run_simulation()
        S_zero = results_zero['S']
        I_zero = results_zero['I']
        
        # zeroTraditionalSpreadRateShouldleadCauseNoTraditionalSpread
        self.assertAlmostEqual(S_zero[-1], 99, places=1, msg="zeroTraditionalSpreadRateTimeEasyInfectionErQuantityShouldProtectionSupportNotChange")
        self.assertAlmostEqual(I_zero[-1], 1, places=1, msg="zeroTraditionalSpreadRateTimeInfectionInfectionErQuantityShouldProtectionSupportNotChange")


if __name__ == '__main__':
    unittest.main()