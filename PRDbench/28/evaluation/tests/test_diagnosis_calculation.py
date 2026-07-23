# -*- coding: utf-8 -*-
"""
Diagnosis score calculation unit test
"""

import pytest
import sys
import os
from datetime import datetime

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from services.diagnosis_service import DiagnosisService
from models.database import Company


class TestDiagnosisCalculation:
    """Diagnosis score calculation test class"""

    def setup_method(self):
        """Setup before test"""
        self.diagnosis_service = DiagnosisService()

        # Create test company object
        self.test_company = Company(
            id=1,
            name="Test Company",
            establishment_date=datetime.strptime("2020-01-01", "%Y-%m-%d").date(),
            registered_capital=1000,
            company_type="Limited Liability Company",
            main_business="Software Development",
            industry="Software and Information Technology Services",
            employee_count=100,
            annual_revenue=5000,
            annual_profit=500,
            asset_liability_ratio=0.4,
            patent_count=5,
            copyright_count=3,
            rd_investment=750,
            rd_revenue_ratio=0.15,
            rd_personnel_ratio=0.3,
            innovation_achievements="Obtained multiple software copyrights",
            internal_control_score=4,
            financial_standard_score=4,
            compliance_training_score=3,
            employment_compliance_score=4,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    def test_funding_gap_score_excellent(self):
        """Test funding gap score - excellent case"""
        # Set excellent financial status
        company = self.test_company
        company.asset_liability_ratio = 0.3 # Low debt ratio
        company.annual_profit = 1000 # High profit
        company.annual_revenue = 5000

        score = self.diagnosis_service._calculate_funding_gap_score(company)
        assert score >= 4.0
        assert score <= 5.0

    def test_funding_gap_score_poor(self):
        """Test funding gap score - poor case"""
        company = self.test_company
        company.asset_liability_ratio = 0.9 # High debt ratio
        company.annual_profit = -100 # Loss

        score = self.diagnosis_service._calculate_funding_gap_score(company)
        assert score <= 2.0
        assert score >= 1.0

    def test_debt_capacity_score_excellent(self):
        """Test debt capacity score - excellent case"""
        company = self.test_company
        company.asset_liability_ratio = 0.2 # Low debt ratio
        company.annual_profit = 800 # High profit
        company.annual_revenue = 5000
        company.registered_capital = 500 # Sufficient capital

        score = self.diagnosis_service._calculate_debt_capacity_score(company)
        assert score >= 4.0
        assert score <= 5.0

    def test_debt_capacity_score_poor(self):
        """Test debt capacity score - poor case"""
        company = self.test_company
        company.asset_liability_ratio = 0.8 # High debt ratio
        company.annual_profit = -200 # Loss
        company.registered_capital = 50 # Insufficient capital

        score = self.diagnosis_service._calculate_debt_capacity_score(company)
        assert score <= 2.5
        assert score >= 1.0

    def test_innovation_score_excellent(self):
        """Test innovation capability score - excellent case"""
        company = self.test_company
        company.patent_count = 15 # Many patents
        company.copyright_count = 8
        company.rd_revenue_ratio = 0.20 # High R&D investment ratio
        company.rd_personnel_ratio = 0.4 # High R&D personnel ratio
        company.innovation_achievements = "Multiple major technical breakthroughs"

        score = self.diagnosis_service._calculate_innovation_score(company)
        assert score >= 4.5
        assert score <= 5.0

    def test_innovation_score_poor(self):
        """Test innovation capability score - poor case"""
        company = self.test_company
        company.patent_count = 0 # No patents
        company.copyright_count = 0
        company.rd_revenue_ratio = 0.01 # Low R&D investment
        company.rd_personnel_ratio = 0.05 # Low R&D personnel ratio
        company.innovation_achievements = None

        score = self.diagnosis_service._calculate_innovation_score(company)
        assert score <= 2.0
        assert score >= 1.0

    def test_management_score_calculation(self):
        """Test management standardization score calculation"""
        company = self.test_company
        company.internal_control_score = 4
        company.financial_standard_score = 3
        company.compliance_training_score = 5
        company.employment_compliance_score = 2

        score = self.diagnosis_service._calculate_management_score(company)
        expected_score = (4 + 3 + 5 + 2) / 4
        assert score == expected_score
        assert score == 3.5

    def test_score_boundaries(self):
        """Test score boundary values"""
        company = self.test_company

        # Test lowest score
        company.asset_liability_ratio = 1.0
        company.annual_profit = -1000
        funding_score = self.diagnosis_service._calculate_funding_gap_score(company)
        assert funding_score >= 1.0

        # Test highest score
        company.asset_liability_ratio = 0.1
        company.annual_profit = 2000
        funding_score = self.diagnosis_service._calculate_funding_gap_score(company)
        assert funding_score <= 5.0

    def test_innovation_score_incremental(self):
        """Test innovation capability score incremental logic"""
        company = self.test_company

        # Base score
        company.patent_count = 0
        company.copyright_count = 0
        company.rd_revenue_ratio = 0.0
        company.rd_personnel_ratio = 0.0
        company.innovation_achievements = None
        base_score = self.diagnosis_service._calculate_innovation_score(company)
        assert base_score == 1.0

        # After adding patents, score should increase
        company.patent_count = 3
        company.copyright_count = 2
        higher_score = self.diagnosis_service._calculate_innovation_score(company)
        assert higher_score > base_score

        # After adding R&D investment, score should further increase
        company.rd_revenue_ratio = 0.12
        even_higher_score = self.diagnosis_service._calculate_innovation_score(company)
        assert even_higher_score > higher_score


if __name__ == "__main__":
 pytest.main([__file__])