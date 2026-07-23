import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from algorithms.content_based import ContentBasedRecommender
from data_old.preprocessor import DataPreprocessor


class TestChineseTextSegmentation:
    """Chinese text segmentation processing unit test"""

    def setup_method(self):
        """Pre-test setup"""
        self.content_recommender = ContentBasedRecommender()
        self.preprocessor = DataPreprocessor()

    def create_chinese_text_data(self):
        """Create test data containing Chinese text"""
        chinese_texts = [
            "AppleiPhone 14 ProSmartphone 256GB DeepEmptyBlackColor",
            "HuaweiMate50 Pro 5GPhone HongMengSystem PhotographyGodDevice",
            "Xiaomi13 UltraLaiKaCameraMachine SnapdragonDragon8Gen2ProcessingDevice",
            "OPPO Find X6 Pro HasselbladSuImagingFlagshipShipPhotographyPhone",
            "vivo X90 Pro+ ZeissSiLightOpticsLensHead UltraNightPersonPortrait",
            "SamStarGalaxy S23 Ultra 5G SmartS PenHandWritePen",
            "OnePlus11 SnapdragonDragon8Gen2 2K 120HzCurvedSurfaceScreenScreen",
            "MeizuZu20 Pro NoBoundaryDesignDesign StarEraMeizuZuDoubleBrandBrand",
            "SonyNiXperia 1 V 4K HDR OLEDDisplayScreen",
            "GoogleGePixel 7 Pro NativeNativeAndroidSystemIntegratedExperience",
            "LenovoXiangRescueRescueErY9000P GamingLaptopComputer",
            "DellErXPS 13 Plus UltraUltraBookLightThinPortablePortable",
            "ASUSStekROG PlayerPlayerCountryDegrees E-sportsGamingBook",
            "HPPDarkShadowEliteLing8 HighPerformanceGamingLaptop",
            "ThinkPad X1 Carbon BusinessOfficeOfficeBook",
            "MacBook Pro 14InchInch M2ChipChipProfessionalEdition",
            "Surface Laptop 5 MicrosoftSoftOfficialOfficialCertifiedCertified",
            "Mechrevo FloodDragon16K E-sportsGamingBook",
            "Shinelon DestroyerDestroyerErDD2 HighEndGamingLaptop",
            "HaseeWarGod Z8-CU7NS Cost-effectiveGamingBook",
            "NikeAir Jordan 1 EconomyClassicRetroBasketball Shoes",
            "AdidasUltraboost 22 RunningStepSportsShoes",
            "New Balance990v5 AmericanMadeLimitedEditionEditionRetroRunningShoes",
            "ConverseAll Star EconomyClassicCanvasShoesTrendyStyle",
            "VansOld Skool Skateboard ShoesStreetHeadTrendyBrand",
            "PumaSuede Classic RetroBoard ShoesClassicEdition",
            "AntaKT7 ThompsonPSenSignatureNameBasketballWarBoot",
            "Li-NingWadeWadeWay10 ProfessionalBasketball Shoes",
            "361Degrees CountryInternationalLineProfessionalRunning Shoes",
            "Xtep RacingSpeed160X MarathonRunningShoes",
            "MideaInverterAir Conditioner 1.5Horse EnergyEnergyQuietSound",
            "GreeBrandYue WallHangingStyleHomeColdWarmAir Conditioner",
            "HaierCommander SmartWiFiControlControlAir Conditioner",
            "AUX GoldClassicSeriesSeries InverterColdWarmAir Conditioner",
            "TCL BedroomRoomAir Conditioner QuickControlColdControlHeat",
            "Hisense ComfortSuitablePlayer SmartInverterAir Conditioner",
            "Changhong YueEnjoySeriesSeries EnergyEnergyEnvironmentProtectionAir Conditioner",
            "Chigo CloudAir Conditioner PhoneAPPRemoteProcessControlControl",
            "Kelon YueYaSeriesSeries QuietSoundComfortSuitableAir Conditioner",
            "Chunlan ClassicEdition TraditionalSystemMachineMechanicalStyleAir Conditioner",
            "Siemens DrumDrumWashing Machine 10KGLargeCapacityEdition",
            "Haier WaveWheelWashing Machine AutomaticAutoAutoHome",
            "Little Swan BiferFiLi HighEndWashCareOneIntegratedMachine",
            "Midea WashDryOneIntegratedMachine SmartDispenseDispense",
            "Panasonic RomeoMiOuSeriesSeries JapaneseStyleEliteEngineering",
            "LG SteamSteamWashing Machine RemoveBacteriaCareProcessorFunction",
            "Bosch EuropeanImported DrumDrumWashing Machine",
            "Whirlpool AmericanStyle LargeCapacityEditionWashing Machine",
            "Sanyo WaveWheelWashing Machine EconomyEconomyImplementationUseType",
            "Commander HaierSubBrandBrand Cost-effectiveWashing Machine"
        ]
        
        items_df = pd.DataFrame({
            'item_id': range(1, len(chinese_texts) + 1),
            'title': chinese_texts,
            'description': [f"This is the detailed description of {text}" for text in chinese_texts],
            'category': ['phone', 'phone', 'phone', 'phone', 'phone', 'phone', 'phone', 'phone', 'phone', 'phone',
                        'computer', 'computer', 'computer', 'computer', 'computer', 'computer', 'computer', 'computer', 'computer', 'computer',
                        'shoes', 'shoes', 'shoes', 'shoes', 'shoes', 'shoes', 'shoes', 'shoes', 'shoes', 'shoes',
                        'appliance', 'appliance', 'appliance', 'appliance', 'appliance', 'appliance', 'appliance', 'appliance', 'appliance', 'appliance',
                        'appliance', 'appliance', 'appliance', 'appliance', 'appliance', 'appliance', 'appliance', 'appliance', 'appliance', 'appliance']
        })
        
        return items_df
    
    def test_chinese_text_segmentation(self):
        """Test Chinese text segmentation functionality"""
        # Prepare test data
        items_df = self.create_chinese_text_data()

        # Test Chinese word segmentation for content-based recommendation
        text_columns = ['title', 'description']
        combined_texts = self.content_recommender._combine_text_features(items_df, text_columns)

        # Verify segmentation results
        assert len(combined_texts) == len(items_df), "Number of segmentation results should match input data"

        # Verify segmentation quality: check for reasonable word separation
        sample_text = combined_texts[0]  # Segmentation result of first item
        assert ' ' in sample_text, "Segmentation result should contain space-separated words"

        # Verify keyword recognition accuracy
        phone_texts = combined_texts[:10]  # Phone category items
        phone_keywords = ['iPhone', 'Huawei', 'Xiaomi', 'OPPO', 'vivo', 'Phone', 'Smart', 'CameraMachine']

        # Calculate proportion of texts containing at least one relevant keyword
        texts_with_keywords = 0
        for text in phone_texts:
            has_keyword = any(keyword in text for keyword in phone_keywords)
            if has_keyword:
                texts_with_keywords += 1

        accuracy = texts_with_keywords / len(phone_texts) if phone_texts else 0
        assert accuracy >= 0.6, f"Segmentation accuracy should be >=60%, actual is {accuracy:.2%}"

        # Verify segmentation diversity for different categories
        categories = ['phone', 'computer', 'shoes', 'appliance']
        category_texts = {}

        for i, category in enumerate(categories):
            start_idx = i * 10
            end_idx = (i + 1) * 10
            category_texts[category] = combined_texts[start_idx:end_idx]

        # Verify each category has specific keywords
        category_keywords = {
            'phone': ['Phone', 'Smart', 'CameraMachine', 'ProcessingDevice', 'Photography'],
            'computer': ['Computer', 'Laptop', 'Gaming', 'ProcessingDevice', 'CPU'],
            'shoes': ['Shoes', 'RunningStep', 'Basketball', 'Sports', 'TrendyTrend'],
            'appliance': ['Air Conditioner', 'Washing Machine', 'Inverter', 'Smart', 'EnergyEnergy']
        }

        for category, texts in category_texts.items():
            keywords = category_keywords[category]
            found_in_category = 0
            for text in texts:
                for keyword in keywords:
                    if keyword in text:
                        found_in_category += 1
                        break

            category_accuracy = found_in_category / len(texts)
            assert category_accuracy >= 0.5, f"{category} category keyword recognition rate should be >=50%, actual is {category_accuracy:.2%}"
    
    def test_preprocessor_text_segmentation(self):
        """Test data preprocessor Chinese text segmentation"""
        # Test data
        test_df = pd.DataFrame({
            'item_id': [1, 2, 3],
            'title': [
                "HuaweiMate50 Pro Smartphone",
                "AppleMacBook Pro LaptopComputer",
                "NikeAir Jordan Basketball Shoes"
            ],
            'description': [
                "ThisIsAHighEndSmartphoneProduct",
                "ProfessionalLevelLaptopComputerDesignPrepare",
                "ClassicRetroBasketballSportsShoes"
            ]
        })

        # Execute text feature processing
        result_df = self.preprocessor.process_text_features(test_df, ['title', 'description'])

        # Verify segmented columns are created
        assert 'title_segmented' in result_df.columns, "Should create title_segmented column"
        assert 'description_segmented' in result_df.columns, "Should create description_segmented column"

        # Verify segmentation results contain space-separated words
        for idx, row in result_df.iterrows():
            assert ' ' in row['title_segmented'], f"Row {idx} title segmentation result should contain spaces"
            assert ' ' in row['description_segmented'], f"Row {idx} description segmentation result should contain spaces"

        # Verify cleaned text columns
        assert 'title_cleaned' in result_df.columns, "Should create title_cleaned column"
        assert 'description_cleaned' in result_df.columns, "Should create description_cleaned column"
    
    def test_segmentation_edge_cases(self):
        """Test segmentation edge cases"""
        # Test empty text
        empty_result = self.preprocessor._segment_chinese_text("")
        assert empty_result == "", "Empty text segmentation should return empty string"

        # Test None value
        none_result = self.preprocessor._segment_chinese_text(None)
        assert none_result == "", "None value segmentation should return empty string"

        # Test English-only text
        english_text = "iPhone 14 Pro Max"
        english_result = self.preprocessor._segment_chinese_text(english_text)
        assert len(english_result.split()) >= 3, "English text should also be correctly segmented"

        # Test mixed Chinese-English text
        mixed_text = "HuaweiMate50 ProSmartphone"
        mixed_result = self.preprocessor._segment_chinese_text(mixed_text)
        assert 'Huawei' in mixed_result, "Mixed Chinese-English text should correctly recognize Chinese part"
        assert 'Mate50' in mixed_result, "Mixed Chinese-English text should preserve English part"
    
    def test_text_cleaning(self):
        """Test text cleaning functionality"""
        # Test text with special characters
        dirty_text = "HuaweiMate50!@#$%^&*()ProSmartphone【OfficialOfficialCorrectBrand】"
        cleaned_result = self.preprocessor._clean_text(dirty_text)

        # Verify special characters are removed
        special_chars = "!@#$%^&*()【】"
        for char in special_chars:
            assert char not in cleaned_result, f"Special character '{char}' should be removed"

        # Verify Chinese, English, and numbers are preserved
        assert 'Huawei' in cleaned_result, "Chinese should be preserved"
        assert 'Mate50' in cleaned_result, "English and numbers should be preserved"
        assert 'Pro' in cleaned_result, "English should be preserved"