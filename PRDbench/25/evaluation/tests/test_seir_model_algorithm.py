import unittest
import sys
import os
import numpy as np

# AddsrcDirectorytoPythonPath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from models.seir_model import SEIRModel


class TestSEIRModelAlgorithm(unittest.TestCase):
    """SEIRModelTypeCoreCoreCalculateMethodTestCategory"""
    
    def setUp(self):
        """TestbeforeStandardPrepare"""
        self.N = 10000  # TotalPersonPortNumber
        self.beta = 0.03  # TraditionalSpreadRate
        self.sigma = 0.1  # LatentlatentPeriodConvertInfectionInfectionRate
        self.gamma = 0.1  # HealthRecoveryRate
        self.days = 160  # ModelSimulationDayNumber
        
    def test_seir_model_core_algorithm(self):
        """TestSEIRModelTypeCoreCoreCalculateMethodImplementationImplementation"""
        # CreateSEIRModelTypeImplementationExample(UseUseDefaultCertifiedConfigure)
        model = SEIRModel()
        
        # RunModelSimulationparallelGetGetResult
        results = model.run_simulation()
        
        # ExtractGetTimeBetweenSequenceSeriesData
        S = results['S']
        E = results['E']
        I = results['I']
        R = results['R']
        time = results['time']
        
        # GetGetConfigureParameter
        N = model.N
        days = len(time) - 1
        
        # Test1: VerifyArrayLengthDegrees
        self.assertEqual(len(S), days + 1, f"SSequenceSeriesLengthDegreesShouldas{days + 1}")
        self.assertEqual(len(E), days + 1, f"ESequenceSeriesLengthDegreesShouldas{days + 1}")
        self.assertEqual(len(I), days + 1, f"ISequenceSeriesLengthDegreesShouldas{days + 1}")
        self.assertEqual(len(R), days + 1, f"RSequenceSeriesLengthDegreesShouldas{days + 1}")
        
        # Test2: VerifyInitialInitialentryPiece
        self.assertEqual(S[0], N - 1, f"InitialInitialEasyInfectionErQuantityShouldas{N-1}")
        self.assertEqual(E[0], 0, "InitialInitialLatentlatentErQuantityShouldas0")
        self.assertEqual(I[0], 1, "InitialInitialInfectionInfectionErQuantityShouldas1")
        self.assertEqual(R[0], 0, "InitialInitialHealthRecoveryErQuantityShouldas0")
        
        # Test3: VerifyconservationFixedlaw S(t) + E(t) + I(t) + R(t) = N
        for t in range(len(S)):
            total = S[t] + E[t] + I[t] + R[t]
            self.assertAlmostEqual(total, N, places=6,
                                 msg=f"TimeBetweenPoint{t}conservationFixedlawFailEffect: Totaland={total}")
        
        # Test4: VerifySingleAdjustness
        # S(t)ShouldSingleAdjustdecrease
        for t in range(1, len(S)):
            self.assertLessEqual(S[t], S[t-1], f"S(t)int={t}TimeviolateReverseSingleAdjustdecreaseness")
        
        # R(t)ShouldSingleAdjustincreaseIncrease
        for t in range(1, len(R)):
            self.assertGreaterEqual(R[t], R[t-1], f"R(t)int={t}TimeviolateReverseSingleAdjustincreaseIncreaseness")
        
        # Test5: VerifySEIRSpecialHasfourStatusConversionlogic
        # E(t)andI(t)allShouldfirstIncreaseafterdecrease,SaveinPeakValue
        E_peak_idx = np.argmax(E)
        I_peak_idx = np.argmax(I)
        
        # LatentlatentErPeakValueShouldinInfectionInfectionErPeakValueofbefore
        self.assertLessEqual(E_peak_idx, I_peak_idx,
                           "LatentlatentErPeakValueShouldinInfectionInfectionErPeakValueofbeforeorSameTimeOutputImplementation")
        
        # Test6: VerifyR0forepidemicSituationShadowResponse
        R0 = results['R0_basic']
        self.assertGreater(R0, 1, f"R0={R0}ShouldLargeAt1")
        
        # becauseAtR0 > 1,epidemicSituationShouldLargeRuleModeloutbreakSend
        max_infected = max(I)
        final_attack_rate = R[-1] / N
        
        self.assertGreater(final_attack_rate, 0.8,
                          f"R0>1TimeMostEndattackRate{final_attack_rate:.3f}Should>80%")
        
        # Test7: VerifyMostEndStatus
        final_S = S[-1]
        final_E = E[-1]
        final_I = I[-1]
        final_R = R[-1]
        
        # MostEndLatentlatentErandInfectionInfectionErShouldInterfacenear0
        self.assertLess(final_E, 10, "MostEndLatentlatentErQuantityShouldverySmall")
        self.assertLess(final_I, 10, "MostEndInfectionInfectionErQuantityShouldverySmall")
        
        # MostEndHealthRecoveryErShouldaccount_forabsoluteLargeManyNumber
        self.assertGreater(final_R, N * 0.8,
                          f"MostEndHealthRecoveryEr{final_R}Shouldaccount_forPersonPort80%toon")
        
        # Test8: VerifyNumberValuestableFixedness(NoNaNorInf)
        for state, name in [(S, 'S'), (E, 'E'), (I, 'I'), (R, 'R')]:
            self.assertTrue(np.all(np.isfinite(state)), f"{name}SequenceSeriesContainsnonHasLimitedNumberValue")
            self.assertTrue(np.all(state >= 0), f"{name}SequenceSeriesContainsNegativeNumber")
            
        # Test9: VerifyModelTypeFoundationBookSpecialfeature(SimpleizationTest)
        # VerifyEandIPeakValueSavein
        E_max = max(E)
        I_max = max(I)
        
        self.assertGreater(E_max, 0, "LatentlatentErShouldSaveinPeakValue")
        self.assertGreater(I_max, 0, "InfectionInfectionErShouldSaveinPeakValue")
        
        # VerifyModelTypeReceiveconverge
        self.assertLess(E[-1], E_max * 0.1, "MostEndLatentlatentErQuantityShouldRemoteSmallAtPeakValue")
        self.assertLess(I[-1], I_max * 0.1, "MostEndInfectionInfectionErQuantityShouldRemoteSmallAtPeakValue")
    
    def test_seir_model_basic_properties(self):
        """TestSEIRModelTypeFoundationBookSpecialness"""
        # CreateModelTypeImplementationExampleparallelRun
        model = SEIRModel()
        results = model.run_simulation()
        
        # Verification ResultsContainsnecessaryKey
        required_keys = ['S', 'E', 'I', 'R', 'time', 'R0_basic']
        for key in required_keys:
            self.assertIn(key, results, f"ResultShouldContains{key}CharacterSegment")
        
        # VerifyR0DesignCalculate
        R0 = results['R0_basic']
        self.assertGreater(R0, 0, "R0ShouldasCorrectNumber")
        self.assertIsInstance(R0, (int, float), "R0ShouldasNumberValueCategoryType")


if __name__ == '__main__':
    unittest.main()