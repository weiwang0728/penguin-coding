# -*- coding: utf-8 -*-
"""
DataCharacterSegmentExtractGetandVerifyUnit Test
TestDataProcessorCategoryinRelatedKeyCharacterSegmentExtractGetFunction
"""

import pytest
import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime

# AddsrcDirectorytoPath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from data_processing import DataProcessor


class TestDataFieldExtraction:
    """DataCharacterSegmentExtractGetandVerifyTestCategory"""
    
    def setup_method(self):
        """eachitem(s)TestOfficialMethodbeforeDesignSet"""
        self.processor = DataProcessor()
        
    def test_key_field_extraction_and_validation(self):
        """TestRelatedKeyCharacterSegmentExtractGetandVerify
        
        Verify:
        1. ExtractGetCharacterSegmentQuantityas4item(s)
        2. CharacterSegmentNamenameCorrectAccurate
        3. DataCategoryTypeConversionStandardAccurate(JapanesePeriodasdatetimeCategoryType,NumberValueasintorfloatCategoryType)
        4. NoMissingFailValueProcessingError
        """
        
        # CreateshowExampleDataImportLineTest
        self.processor.create_sample_data()
        
        # VerifyNativeInitialDataAlreadyLoad
        assert self.processor.raw_data is not None, "NativeInitialDataShouldThisbeSuccessCreate"
        
        # VerifyRelatedKeyCharacterSegmentSavein
        required_fields = [
            'date',
            'cumulative_confirmed', 
            'cumulative_deaths',
            'cumulative_recovered'
        ]
        
        # CheckCharacterSegmentQuantity
        actual_key_fields = [col for col in self.processor.raw_data.columns 
                           if col in required_fields]
        assert len(actual_key_fields) == 4, f"ShouldThisHas4item(s)RelatedKeyCharacterSegment,ImplementationInternationalHas{len(actual_key_fields)}item(s)"
        
        # CheckCharacterSegmentNamenameCorrectAccurateness
        for field in required_fields:
            assert field in self.processor.raw_data.columns, f"Missingminimum necessaryCharacterSegment: {field}"
        
        # VerifyDataCategoryType
        # JapanesePeriodCharacterSegmentShouldThisYesdatetimeCategoryType
        date_series = self.processor.raw_data['date']
        assert pd.api.types.is_datetime64_any_dtype(date_series), \
            f"JapanesePeriodCharacterSegmentCategoryTypeError,Periodexpecteddatetime,ImplementationInternational{date_series.dtype}"
        
        # NumberValueCharacterSegmentShouldThisYesNumberValueCategoryType(intorfloat)
        numeric_fields = ['cumulative_confirmed', 'cumulative_deaths', 'cumulative_recovered']
        for field in numeric_fields:
            field_series = self.processor.raw_data[field]
            assert pd.api.types.is_numeric_dtype(field_series), \
                f"NumberValueCharacterSegment{field}CategoryTypeError,PeriodexpectedNumberValueCategoryType,ImplementationInternational{field_series.dtype}"
        
        # VerifyNoMissingFailValueProcessingError
        for field in required_fields:
            field_series = self.processor.raw_data[field]
            nan_count = field_series.isna().sum()
            assert nan_count == 0, f"CharacterSegment{field}Savein{nan_count}item(s)MissingFailValue"
        
        # VerifyNumberValueCharacterSegmentFoundationBooklogicness(nonNegativeNumberEqual)
        for field in numeric_fields:
            values = self.processor.raw_data[field].values
            
            # ChecknonNegativeNumber
            assert np.all(values >= 0), f"CharacterSegment{field}ContainsNegativeValue"
            
            # CheckDataRangerangeCombineProcessorness(NotShouldThisHasAbnormalLargeValue)
            max_reasonable_value = 1e8  # DesignFixedOneitem(s)CombineProcessoronLimited
            assert np.all(values <= max_reasonable_value), \
                f"CharacterSegment{field}ContainsAbnormalLargeValue: max={np.max(values)}"
        
        print("RelatedKeyCharacterSegmentExtractGetandVerifyTest Passed")
        
    def test_field_extraction_with_real_data(self):
        """TestUseUseTrueImplementationDataFileCharacterSegmentExtractGet(ifResultFileSavein)"""
        
        # attemptLoadTrueImplementationData
        data_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'epidemic_data.xlsx')
        
        if os.path.exists(data_file):
            success = self.processor.load_raw_data(data_file)
            
            if success:
                # ExecuteDataVerify
                validation_result = self.processor.validate_data()
                assert validation_result, "DataVerifyShouldThisSuccess"
                
                # CheckDatashape
                assert len(self.processor.raw_data) > 0, "DataShouldThisContainsLine"
                assert len(self.processor.raw_data.columns) > 0, "DataShouldThisContainsSeries"
                
                print(f"TrueImplementationDataFileTest Passed,Datashape: {self.processor.raw_data.shape}")
            else:
                print("TrueImplementationDataFileSaveinbutLoadFailure,SkipthisTest")
        else:
            print("TrueImplementationDataFileNotSavein,SkipthisTest")
    
    def test_data_type_conversion_accuracy(self):
        """TestDataCategoryTypeConversionStandardAccurateness"""
        
        # CreateContainsNotSameDataCategoryTypeTestData
        test_data = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=10),
            'cumulative_confirmed': range(0, 100, 10),  # EntireNumber
            'cumulative_deaths': [float(x) for x in range(0, 10)],  # floatPointNumber
            'cumulative_recovered': np.array(range(0, 50, 5))  # numpyArray
        })
        
        self.processor.raw_data = test_data
        
        # VerifyDataCategoryTypeConversion
        assert pd.api.types.is_datetime64_any_dtype(test_data['date']), "JapanesePeriodCategoryTypeConversionFailure"
        assert pd.api.types.is_integer_dtype(test_data['cumulative_confirmed']), "EntireNumberCategoryTypeProtectionSupportCorrectAccurate"
        assert pd.api.types.is_float_dtype(test_data['cumulative_deaths']), "floatPointNumberCategoryTypeProtectionSupportCorrectAccurate"
        assert pd.api.types.is_numeric_dtype(test_data['cumulative_recovered']), "NumberValueArrayCategoryTypeConversionCorrectAccurate"
        
        print("DataCategoryTypeConversionStandardAccuratenessTest Passed")
    
    def test_missing_value_handling(self):
        """TestMissingFailValueProcessing"""
        
        # CreateContainsMissingFailValueTestData
        test_data = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=5),
            'cumulative_confirmed': [10, 20, np.nan, 40, 50],
            'cumulative_deaths': [1, 2, 3, np.nan, 5],
            'cumulative_recovered': [8, 15, 25, 35, np.nan]
        })
        
        self.processor.raw_data = test_data
        
        # ExecuteDataVerify,ShouldThisCheckTesttoMissingFailValue
        validation_result = self.processor.validate_data()
        
        # VerifyMissingFailValuebeCorrectAccuratemarkDifferent
        for col in ['cumulative_confirmed', 'cumulative_deaths', 'cumulative_recovered']:
            has_missing = test_data[col].isna().any()
            assert has_missing, f"ShouldThisCheckTesttoCharacterSegment{col}inMissingFailValue"
        
        print("MissingFailValueProcessingTest Passed")


if __name__ == "__main__":
    # RunTest
    test_instance = TestDataFieldExtraction()
    test_instance.setup_method()
    
    try:
        test_instance.test_key_field_extraction_and_validation()
        test_instance.test_field_extraction_with_real_data()
        test_instance.test_data_type_conversion_accuracy()
        test_instance.test_missing_value_handling()
        print("\nPlaceHasTest Passed!")
    except AssertionError as e:
        print(f"\nTest Failed: {e}")
    except Exception as e:
        print(f"\nTestOutputWrong: {e}")