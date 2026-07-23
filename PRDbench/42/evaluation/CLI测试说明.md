# Enterprise Talent Training and Skill Analysis System - pureCommandLineTesttest suite

## 🎯 pure command-lineadvantages

Based on your requirements, I have alreadyEntireitem(s)Testtest suiteAdjustEntireas**pure command-line interface**, ToolHasthe followingadvantages: 

### ✅ AutomatedTestfriendly
- PlaceHasFunctionPassCLICommandExecute
- OutputResultDirectInterfaceinControlconsole display
- NoGUIInterface, No web-page dependencies
- SuitableCombineCI/CDSetSuccessandBatchTest

### ✅ lightweight deployment
- MostSmallizationDependDependPackagerequested
- no need forweb service
- Caninany supported Python environment
- SuitableCombineservice-sideEndandCapacityDeviceizationdeployment

## 📋 CoreCLICommanddemo

### 1. SystemStartVerify
```bash
# Core Functionalitydemo(RecommendationUseAtTest)
python src/demo.py

# CLIToolhelp
python src/cli.py --help
```

### 2. DataManagementCommand
```bash
# Importsurvey data
python src/cli.py data import-data -f evaluation/test_survey.csv -c "TestEnterprise" -t survey

# Importinterview data
python src/cli.py data import-data -f evaluation/test_interview.txt -c "TestEnterprise" -t interview

# ExportData
python src/cli.py data export-data -c "TestEnterprise" -t survey -f csv -o output.csv

# SeriesOutputData
python src/cli.py data list-data -c "TestEnterprise"
```

### 3. Data AnalysisCommand
```bash
# CauseSubAnalysis
python src/cli.py analysis factor -c "TestEnterprise" -f 3 -r varimax

# GroupBetweenBiferCompareAnalysis
python src/cli.py analysis compare -c "TestEnterprise" -g management_level

# CameraRelatednessAnalysis
python src/cli.py analysis correlation -c "TestEnterprise"

# SeriesOutputAnalysisResult
python src/cli.py analysis list-results
```

### 4. Report GenerationCommand
```bash
# Generate enterprise report
python src/cli.py report generate -c "TestEnterprise" -f txt

# GenerateAnalysis Report
python src/cli.py report generate -a 1 -a 2 -f docx

# SeriesOutputPlaceHasReport
python src/cli.py report list-reports
```

### 5. SystemManagementCommand
```bash
# InitialInitializationSystem
python src/cli.py system init

# Create manager
python src/cli.py system create-admin

# SystemStatusCheck
python src/cli.py system status
```

## 🔧 Environment Configuration

### FoundationFoundationDependDependinstall
```bash
# installFoundationFoundationDependDependPackage(Alreadycompatibility optimization)
pip install -r src/requirements_basic.txt
```

### requirements_basic.txt Contains: 
- **Data Processing**: pandas, numpy, scikit-learn, scipy
- **SystemDesignAnalysis**: factor-analyzer
- **FileProcessing**: python-docx, openpyxl
- **visualization**: matplotlib(used only forchartGenerate, NotDisplayGUI)
- **CLITool**: click
- **Testframework**: pytest
- **other tools**: loguru, python-dotenv

## 📊 TestExecuteOfficialStyle

### OfficialStyle1: complete test suite
```bash
python evaluation/run_tests.py
```

### OfficialStyle2: single functional test
```bash
# SystemStartTest
python src/demo.py

# Data ImportTest
python src/cli.py data import-data -f evaluation/test_survey.csv -c "TestEnterprise" -t survey

# AnalysisFunctional Test
python src/cli.py analysis factor -c "TestEnterprise" -f 3 -r varimax

# chartGenerateTest(NoGUIDisplay)
python evaluation/tests/generate_histogram.py
```

### OfficialStyle3: Unit Test
```bash
# RunPlaceHasUnit Test
pytest evaluation/tests/ -v

# RunSpecialFixedTest
pytest evaluation/tests/test_skill_dimensions.py -v
```

## 🎯 pureCommandLineOutputshowExample

### demo.py OutputshowExample: 
```
╔══════════════════════════════════════════════════════════════╗
║        🎯 Enterprise Talent Training and Skill Analysis System v1.0.0                ║
╚══════════════════════════════════════════════════════════════╝

✅ SuccessLoad 20 sample data records

📊 descriptiveSystemDesignAnalysis:
skillDimensionRepublic            AverageValue       MarkStandardDifference      MostSmallValue      MostLargeValue
-------------------------------------------------------
leadershipandmotivationskill         3.98     0.56     3.10     4.90
DesignplanGrouporganizationandProtocolAdjustskill       3.94     0.37     3.30     4.60
DecisionandcreateNewskill         3.91     0.44     3.10     4.60
professionalandControlskill         3.96     0.39     3.20     4.80

⚖️  GroupBetweenBiferCompareAnalysis(AccordingManagementLayerLevel):
LayerLevel       sampleNumber      leadership motivation       DesignplanGrouporganization       DecisioncreateNew       professionalControl
----------------------------------------------------------------------
InitialLevel       8        3.41       3.59       3.55       3.62
inLevel       5        4.00       4.00       3.90       4.12
HighLevel       7        4.60       4.30       4.33       4.23

✅ ReportAlreadyGenerate: Analysis Report_20250901_144756.txt
```

### CLICommandOutputshowExample: 
```bash
$ python src/cli.py data import-data -f test.csv -c "enterpriseA" -t survey
✅ Data ImportSuccess
📊 ImportSystemDesign:
   - TotalRecordNumber: 50
   - HasEffectRecord: 48
   - NoEffectRecord: 2
   - ImportTimeBetween: 2025-01-15 14:30:25

$ python src/cli.py analysis factor -c "enterpriseA" -f 3 -r varimax
🔬 CorrectinExecuteCauseSubAnalysis...
✅ CauseSubAnalysisCompleteSuccess
📊 AnalysisResult:
   - CauseSubQuantity: 3
   - rotation method: varimax
   - explanationOfficialDifference: 78.5%
   - KMOValue: 0.856
   - BartlettCheckExperience: p < 0.001
```

## 🧪 Test CaseClassification

### shell interaction test(12item(s))
- SystemStartandCLIhelp
- Data Import(CSV、Excel、Word、TextBook)
- Data Analysis(CauseSubAnalysis、ParameterDesignSet、SystemDesignCheckExperience)
- Data ExportandBiferCompareAnalysis

### Unit Test(13item(s))
- skillDimensionRepublicManagement
- sample filteringandmetadata annotation
- dashboardFunction(data processing logic)
- EditionBookManagement

### FileBiferCompareTest(7item(s))
- chartGenerate(PNG、SVGFormatStyle)
- Data Export(CSV、ExcelFormatStyle)
- Report Generation

## 💡 pureCommandLineadvantages

1. **Automatedfriendly**: PlaceHasOperationallcanPassScriptAutomated
2. **assetslow resource usage**: NoGUIInterface, InternalSaveusageUseSmall
3. **deploymentSimpleSingle**: no need forweb serviceandbeforeEndassets
4. **TeststableFixed**: avoid instability caused by GUI-related factors
5. **CI/CDSetSuccess**: CompleteAmericanSuitableCombineSupportContinueSetSuccessEnvironment
6. **cross-platform**: inany supported Python system

## 🚀 QuickStarting

```bash
# 1. install dependencies
pip install -r src/requirements_basic.txt

# 2. Systemdemo
python src/demo.py

# 3. viewCLIhelp
python src/cli.py --help

# 4. RunTest
python evaluation/run_tests.py

# 5. Unit Test
pytest evaluation/tests/ -v
```

thispureCommandLinetest suiteCompleteAutomaticMeetsAutomatedTestrequested, PlaceHasFunctionallPassCLIImplementationImplementation, OutputResultDirectInterfaceinControlconsole display, especially suitable forAutomatedTestandCI/CDSetSuccess.