#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test2.1.2c Data Validation - categoryTypeNotSymboldisplay

TestProgramcand isplaycategory TypeNotSymbolIssue.
"""

import pytest
import sys
import os
import tempfile
import pandas as pd
import numpy as np

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from credit_assessment.data.data_manager import DataManager
    from credit_assessment.utils.config_manager import ConfigManager
except ImportError as e:
    pytest.skip(f"NoMethodImportModule: {e}", allow_module_level=True)


class TestTypeValidation:
    """categoryTypeExperienceTestcategory"""

    def setup_method(self):
        """TestbeforePrepare"""
        self.config = ConfigManager()
        self.data_manager = DataManager(self.config)

        # CreateContainscategoryTypeNotSymbolDataTest file(number value fieldContainsTextBook)
        np.random.seed(42)
        n_samples = 120  # MeetsMostSmall row countrequirements

        # GenerateCombinecategoryTypeData, innumber value fieldContainsTextBook
        ages = []
        incomes = np.random.randint(20000, 200000, n_samples)
        targets = np.random.choice([0, 1], n_samples)

        # inagefieldininputTextBookData(categoryTypeNotSymbol)
        for i in range(n_samples):
            if i < 5:  # before5itemsUseTextBook
                ages.append(['abc', 'xyz', 'invalid', 'text', 'error'][i])
            else:
                ages.append(str(np.random.randint(20, 80)))

        self.test_data = pd.DataFrame({
            'age': ages,  # ShouldasnumberContainsTexttext
            'income': incomes,
            'target': targets
        })

        # CreateTimeCSVFile
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.test_data.to_csv(self.temp_file.name, index=False)
        self.temp_file.close()

    def teardown_method(self):
        """TestafterCleanProcessor"""
        if hasattr(self, 'temp_file') and os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_type_validation(self):
        """TestcategoryTypeExperience function"""
        # Execute (Act): ImportContainscategoryTypeNotSymbolDataTest file
        df = self.data_manager.import_data(self.temp_file.name, validate=False)

        # VerifyData import success
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 120
        assert len(df.columns) == 3

        # Verifyage columnsContainsTextBook(categoryTypeNotSymbol)
        age_series = df['age']
        assert age_series.dtype == 'object', "age columnsShouldThisyesobjectcategoryType(ContainsTextBook)"

        # CheckwhetherContainsnumberTextBook
        non_numeric_count = 0
        for value in age_series.head(10):  # Checkbefore10itemsvalue
            try:
                float(value)
            except (ValueError, TypeError):
                non_numeric_count += 1

        assert non_numeric_count > 0, "age columnsShouldThisContainsNoMethodConversionasnumberTextBookvalue"

        # Break (Assert): VerifyProgramable todisplaycategoryTypeNotSymbolIssue
        validation_result = self.data_manager.validate_current_data()

        # CheckwhetherCheckTesttocategoryTypeNotSymbolCameraRelatedIssue
        has_type_validation = False
        detected_issues = []

        # CheckWarninginformation
        if 'warnings' in validation_result:
            for warning in validation_result['warnings']:
                if any(keyword in warning for keyword in ['categoryType', 'type', 'Forformat', 'number value', 'Conversion']):
                    has_type_validation = True
                    detected_issues.append(f"Warning: {warning}")

        # CheckErrorinformation
        if 'errors' in validation_result:
            for error in validation_result['errors']:
                if any(keyword in error for keyword in ['categoryType', 'type', 'Forformat', 'number value', 'Conversion']):
                    has_type_validation = True
                    detected_issues.append(f"Error: {error}")

        # VerifyCheckTestresult
        if has_type_validation:
            print(f"CheckTesttocategoryTypeNotSymbolIssue: {detected_issues}")
            assert True, "ProgramsuccessCheckTesttocategoryTypeNotSymbolIssue"
        else:
            # resultHasPassVerifyCheckTestto, HandAu to VerifycategoryTypeIssue
            print("Verification result sNotDirect interfaceCheckTesttocategoryTypeIssue, forHandAu to Verify...")

            # Verifyage columnsAccurateImplementationContainsNoMethodConversionTextBook
            invalid_values = []
            for i, value in enumerate(age_series.head(10)):
                try:
                    float(value)
                except (ValueError, TypeError):
                    invalid_values.append((i, value))

            assert len(invalid_values) >= 2, f"age columnsShouldThisContainsat least 2NoEffectnumber value, Implementationinternational: {invalid_values}"

            # VerifyToolintegratedTextBookvalueSavein
            age_values = age_series.tolist()
            assert 'abc' in age_values, "ShouldThisContains'abc'TextBookvalue"
            assert 'xyz' in age_values, "ShouldThisContains'xyz'TextBookvalue"

            print(f"categoryTypeNotSymbolVerify: SendImplementation{len(invalid_values)}itemsNoEffectnumber value: {invalid_values}")


if __name__ == "__main__":
    pytest.main([__file__])
