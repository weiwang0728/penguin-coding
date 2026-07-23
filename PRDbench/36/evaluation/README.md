# Keigo HigashinoSmallnovel textminingandLanguageDefinitionAnalysisTool - TestOfficialCase

## Overview

BookTestOfficialCaseContainsforKeigo HigashinoSmallnovel textminingandLanguageDefinitionAnalysisToolCompleteEntiretest plan, coverCoveragePlaceHasFunctionPointVerify.

## FileResultStructure

```
evaluation/
├── detailed_test_plan.json     # detailedtest plan
├── input_files/               # TestOutputInputFile
│   ├── *.in                  # interactiveTestOutputInput
│   ├── *.txt                 # TestTextBookFile
│   └── ...
├── expected_output/           # Expected OutputFile
│   └── expected_results.txt   # expectedAnalysisResult
├── tests/                     # Unit TestFile
│   ├── test_entity_recognition.py
│   ├── test_output_format.py
│   ├── test_word2vec.py
│   └── test_relationship_reasoning.py
└── README.md                  # BookFile
```

## TestCategoryTypeDescription

### 1. Shell Interaction Test
UseAtTestrequireModelSimulationUserandCommandLineImportLineTrueImplementationinteractiveFunction.

**RunOfficialStyle: **
```bash
cd src
python main.py < ../evaluation/input_files/menu_test.in
```

### 2. Unit Test Test
UseAtVerifySpecialFixedFunctionNumberorCategoryFunction.

**RunOfficialStyle: **
```bash
cd src
pytest ../evaluation/tests/test_entity_recognition.py::test_person_name_recognition
```

### 3. File Comparison Test
UseAtVerifyProgramGenerateOutputFileYesNoCorrectAccurate.

**RunOfficialStyle: **
```bash
cd src
python main.py < ../evaluation/input_files/save_results_test.in
# thenafterBiferCompareGenerateFileandExpected OutputFile
```

## MainTestPoint

### ProgramStartandMenu (0.1)
- VerifyProgramEnergyNormalStartandDisplay7item(s)MenuOption

### FilePathFunction (1.1-1.3)
- MenuaccessTest
- FilePathHasEffectnessvalidation experience
- FileCodeCodeAutoAutoCheckTest(GBK/UTF-8)

### entity recognition extraction (2.1-2.7)
- Menuaccess
- PersonObjectfull namerecognize (nr)
- place namerecognize (ns)
- TimeBetweenTabletime recognitionDifferent (t)
- profession recognitionDifferent (nn)
- ImportDegreesDisplay
- inBreakSupportSupport
- StatusReversefeedback
- historyRecordSaveandRecoveryUse
- OutputFormatStyleVerify

### frequencySystemDesignAnalysis (3.1-3.7)
- Menuaccess
- frequencySystemDesignandranking listGenerate
- ImplementationIntegratedCategoryTypefilter selection(PersonObject/location/TimeBetween/profession)
- frequencyRegionBetweenfilter selection
- GroupCombinefilter selectionentries
- SortFunction
- Dividepaginated display

### semantic similarity analysis (4.1-4.5)
- Menuaccess
- PersonObjectImplementationIntegratedSelectChoose
- Word2VecModelTypeCalculateMethodUseUse
- Word2VecParameterConfigureVerify
- similarityDesignCalculateandranking
- HighsimilarityImplementationIntegratedDeepDegreesAnalysis

### RelatedSeriesPushProcessorAnalysis (5.1-5.5)
- Menuaccess
- CategoryBiferPushProcessorQueryFormatStyleparsing
- DirectionEditionEmptyBetweenCategoryBiferPushProcessorCalculateMethod (D=C+B-A)
- relationship pattern recognition
- RelatedSeriesModelStyleSystemDesignAnalysis

### other functions (6.1-6.4)
- OutputInputHasEffectnessvalidation experience
- TableFormatizationdisplayOption
- ResultSaveFunction
- SavePathAutoFixedDefinition

## RunPlaceHasTest

### RunUnit Test
```bash
cd src
pytest ../evaluation/tests/ -v
```

### RuninteractiveTestexample
```bash
cd src
python main.py < ../evaluation/input_files/menu_test.in
python main.py < ../evaluation/input_files/file_path_validation_test.in
python main.py < ../evaluation/input_files/entity_extraction_menu_test.in
```

## TestData

### OutputInputFile
- `test_novel.txt`: ContainsPersonObject, location, TimeBetween, professionImplementationIntegratedTestSmallnovel
- `test_novel_gbk.txt`: GBKCodeCodeTestFile
- `test_novel_utf8.txt`: UTF-8CodeCodeTestFile
- `person_name_test.txt`: PersonObjectfull nameTestData
- `location_test.txt`: place nameTestData
- `time_test.txt`: TimeBetweenTableexpressionTestData
- `profession_test.txt`: profession titleTestData

### interactiveOutputInputFile
- `*.in`: EachTypeFunctionModelSimulationUserOutputInputSequenceSeries

## Notes

1. RunTestbeforepleaseAccurateProtectionalready installedrequiredDependDepend: 
   ```bash
   pip install pytest numpy
   ```

2. someTestCanEnergyrequire additionalDependDepend(ifgensim), ifResultif not installed, it willAutoAutoSkipCameraRelatedTest.

3. interactiveTestUseUseOutputInputWeightFixedDirection, AccurateProtectionOutputInputFileFormatStyleCorrectAccurate.

4. FilePathTestrequireAccurateProtectionTestFileSaveinAtCorrectAccuratePositionSet.

## Test ResultsEvaluation

eachTestPointallHasforShouldScoreMarkStandard: 
- 2Divide: CompleteAutomaticSymbolCombineRequirements
- 1Divide: partialDivideSymbolCombineRequirements
- 0Divide: NotSymbolCombineRequirements

detailedScoreMarkStandardplease refer to `metric.json` File.
