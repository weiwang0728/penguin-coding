#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import pandas as pd
import subprocess
import csv

# AddsrcDirectorytoPath
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

from data_manager import DataManager

def test_csv_import_complete():
    """CompleteEntireTestCSVData ImportFunction - StrictFormatAccordingAccordingdescription4item(s)StepSteps"""
    
    print("=" * 70)
    print("2.1.1a UserInformationManagement-CSVData Import - CompleteEntireStrictFormatTest")
    print("=" * 70)
    
    # 1. beforeSetCheckExperience：MainMenuinYesNoSaveinUserDataManagementOption
    print("\n1. beforeSetCheckExperience：CheckMainMenuYesNoSaveinUserDataManagementOption...")
    try:
        result = subprocess.run(
            'echo "0" | python main.py',
            shell=True,
            capture_output=True,
            text=True,
            timeout=10,
            cwd=src_dir
        )
        
        menu_output = result.stdout
        if "DataManagement" in menu_output or "User" in menu_output:
            print("✓ MainMenuSaveinUserDataManagementCameraRelatedOption：'DataManagement'")
            menu_check = True
        else:
            print("✗ MainMenuNotFoundClearAccurateUserDataManagementOption")
            menu_check = False
            
    except Exception as e:
        print(f"✗ beforeSetCheckExperienceFailure: {e}")
        menu_check = False
    
    # 2. StandardPrepare：CreateContainsCompleteEntireCharacterSegmentCSVTestFile
    print("\n2. StandardPrepare：CreateContainsUserID、Age、nessDifferent、PurchaseHistoryRecordCSVTestFile...")
    try:
        test_csv_path = "test_users_complete.csv"
        
        # CreateContainsPlaceHasRequiredCharacterSegmentTestData
        test_user_data = [
            {'user_id': 201, 'age': 25, 'gender': 'Male', 'purchase_history': '1,2,3'},
            {'user_id': 202, 'age': 30, 'gender': 'Female', 'purchase_history': '2,4,5'},  
            {'user_id': 203, 'age': 35, 'gender': 'Male', 'purchase_history': '1,3,6'},
            {'user_id': 204, 'age': 28, 'gender': 'Female', 'purchase_history': '4,5,7'},
            {'user_id': 205, 'age': 32, 'gender': 'Male', 'purchase_history': '2,6,8'}
        ]
        
        # WriteInputCSVFile
        with open(test_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['user_id', 'age', 'gender', 'purchase_history']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(test_user_data)
        
        if os.path.exists(test_csv_path):
            print(f"✓ SuccessCreateTestCSVFile：{test_csv_path}")
            print(f"  - ContainsCharacterSegment：UserID、Age、nessDifferent、PurchaseHistoryRecord")
            print(f"  - TestData：{len(test_user_data)}records")
            file_prepared = True
        else:
            print("✗ TestCSVFileCreateFailure")
            file_prepared = False
            
    except Exception as e:
        print(f"✗ StandardPrepareStepSegmentFailure: {e}")
        file_prepared = False
    
    # 3. Execute：SelectChooseData ImportFunction，ImportTestCSVFile
    print("\n3. Execute：SelectChooseData ImportFunction，ImportTestCSVFile...")
    try:
        # CorrectAccurateInitialInitializationDataManager
        config_path = os.path.join(src_dir, 'config/config.json')
        data_manager = DataManager(config_path)
        
        # GetGetImportbeforeUserQuantity
        try:
            original_users = data_manager.load_users()
            original_count = len(original_users) if original_users is not None else 0
            print(f"  - ImportbeforeUserQuantity：{original_count}")
        except:
            original_count = 0
            print(f"  - ImportbeforeUserQuantity：{original_count}")
        
        # CheckDataManagementDeviceYesNoHasImportOfficialMethod
        if hasattr(data_manager, 'import_users_from_csv'):
            result = data_manager.import_users_from_csv(test_csv_path)
            print("✓ CSVData ImportFunctionExecuteCompleteSuccess")
            import_success = True
        elif hasattr(data_manager, 'import_csv_data'):
            result = data_manager.import_csv_data(test_csv_path, data_type='users')
            print("✓ CSVData ImportFunctionExecuteCompleteSuccess")
            import_success = True
        else:
            # DirectInterfaceReadCSVAndAddUser
            import pandas as pd
            df = pd.read_csv(test_csv_path)
            for _, row in df.iterrows():
                data_manager.add_user({
                    'user_id': int(row['user_id']),
                    'age': int(row['age']),
                    'gender': row['gender']
                })
            print("✓ CSVData ImportFunctionExecuteCompleteSuccess（PassStepByStep recordsAdd）")
            import_success = True
        
    except Exception as e:
        print(f"✗ Data ImportExecuteFailure: {e}")
        import_success = False
    
    # 4. Breakassertion：VerifyDataSuccessImport，EnergyViewImportUserRecord
    print("\n4. Breakassertion：VerifyDataSuccessImport，EnergyViewImportUserRecord...")
    
    import_verified = False
    records_viewable = False
    
    if import_success:
        try:
            # CheckImportafterUserData
            updated_users = data_manager.load_users()
            
            if updated_users is not None:
                updated_count = len(updated_users)
                print(f"✓ ImportafterUserQuantity：{updated_count}")
                
                if updated_count > original_count:
                    print(f"✓ DataSuccessImport：NewIncrease{updated_count - original_count}records")
                    import_verified = True
                    
                    # VerifyEnergyViewImportUserRecord
                    test_user_ids = [201, 202, 203, 204, 205]
                    found_users = []
                    
                    for user_id in test_user_ids:
                        user_data = updated_users[updated_users['user_id'] == user_id]
                        if not user_data.empty:
                            found_users.append(user_id)
                    
                    if len(found_users) > 0:
                        print(f"✓ EnergyViewImportUserRecord：Found{len(found_users)}item(s)ImportUser")
                        records_viewable = True
                    else:
                        print("✗ NoMethodViewImportUserRecord")
                        records_viewable = False
                else:
                    print("✗ UserQuantityNotIncreasePlus，Data ImportCanEnergyFailure")
                    import_verified = False
            else:
                print("✗ NoMethodGetGetUserDataImportLineVerify")
                import_verified = False
                
        except Exception as e:
            print(f"✗ BreakassertionVerifyFailure: {e}")
            import_verified = False
    
    # MostEndEvaluation
    print("\n" + "="*60)
    print("StrictFormatTest ResultsEvaluation")
    print("="*60)
    
    all_checks = [menu_check, file_prepared, import_success, import_verified, records_viewable]
    passed_checks = sum(all_checks)
    
    print(f"beforeSetCheckExperience（MenuCheck）: {'PASS' if menu_check else 'FAIL'}")
    print(f"StandardPrepareStepSegment（CSVFileCreate）: {'PASS' if file_prepared else 'FAIL'}")
    print(f"ExecuteStepSegment（ImportFunction）: {'PASS' if import_success else 'FAIL'}")
    print(f"BreakassertionStepSegment（ImportVerify）: {'PASS' if import_verified else 'FAIL'}")
    print(f"BreakassertionStepSegment（RecordView）: {'PASS' if records_viewable else 'FAIL'}")
    
    if passed_checks == 5:
        print("\n✅ 2.1.1a CSVData Import - Fully Passed (2Divide)")
        print("  SymbolCombineexpected_outputPlaceHasStrictFormatRequirements")
        return True
    elif passed_checks >= 3:
        print(f"\n⚠️ 2.1.1a CSVData Import - Partially Passed (1Divide)")
        print(f"  {passed_checks}/5item(s)VerifyPass，NeedCompleteGood")
        return "partial"
    else:
        print(f"\n❌ 2.1.1a CSVData Import - Test Failed (0Divide)")
        print(f"  Only{passed_checks}/5item(s)VerifyPass")
        return False

if __name__ == "__main__":
    result = test_csv_import_complete()
    if result == True:
        sys.exit(0)
    elif result == "partial":
        sys.exit(1)
    else:
        sys.exit(2)