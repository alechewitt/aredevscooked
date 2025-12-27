"""Tests for configuration module."""

import pytest
from aredevscooked.utils.config import (
    IT_CONSULTANCIES,
    BIG_TECH_COMPANIES,
    AI_LABS,
    HEADCOUNT_THRESHOLDS,
    JOB_POSTING_THRESHOLDS,
)


class TestCompanyLists:
    """Test company configuration lists."""

    def test_it_consultancies_count(self):
        """IT consultancies should have exactly 7 companies."""
        assert len(IT_CONSULTANCIES) == 7

    def test_it_consultancies_have_required_fields(self):
        """Each IT consultancy should have name and ticker."""
        for company in IT_CONSULTANCIES:
            assert "name" in company
            assert "ticker" in company
            assert isinstance(company["name"], str)
            assert isinstance(company["ticker"], str)
            assert len(company["name"]) > 0
            assert len(company["ticker"]) > 0

    def test_it_consultancies_names(self):
        """Verify specific IT consultancy names."""
        company_names = [c["name"] for c in IT_CONSULTANCIES]
        expected_names = [
            "HCLTech",
            "LTIMindtree",
            "Cognizant",
            "Infosys",
            "TCS",
            "Tech Mahindra",
            "Wipro",
        ]
        assert set(company_names) == set(expected_names)

    def test_big_tech_count(self):
        """Big tech companies should have exactly 5 companies."""
        assert len(BIG_TECH_COMPANIES) == 5

    def test_big_tech_have_required_fields(self):
        """Each big tech company should have name."""
        for company in BIG_TECH_COMPANIES:
            assert "name" in company
            assert isinstance(company["name"], str)
            assert len(company["name"]) > 0

    def test_big_tech_names(self):
        """Verify specific big tech company names."""
        company_names = [c["name"] for c in BIG_TECH_COMPANIES]
        expected_names = ["Microsoft", "Meta", "Apple", "Amazon", "NVIDIA"]
        assert set(company_names) == set(expected_names)

    def test_ai_labs_count(self):
        """AI labs should have exactly 3 companies."""
        assert len(AI_LABS) == 3

    def test_ai_labs_have_required_fields(self):
        """Each AI lab should have name and greenhouse_board."""
        for company in AI_LABS:
            assert "name" in company
            assert "greenhouse_board" in company
            assert isinstance(company["name"], str)
            assert isinstance(company["greenhouse_board"], str)
            assert len(company["name"]) > 0
            assert len(company["greenhouse_board"]) > 0

    def test_ai_labs_names(self):
        """Verify specific AI lab names."""
        company_names = [c["name"] for c in AI_LABS]
        expected_names = ["DeepMind", "Anthropic", "OpenAI"]
        assert set(company_names) == set(expected_names)


class TestThresholds:
    """Test threshold configurations."""

    def test_headcount_thresholds_structure(self):
        """Headcount thresholds should have all badge levels."""
        expected_levels = ["strong", "neutral", "reasonably_weak", "weak", "collapsing"]
        for level in expected_levels:
            assert level in HEADCOUNT_THRESHOLDS

    def test_headcount_thresholds_values(self):
        """Headcount thresholds should match specification."""
        assert HEADCOUNT_THRESHOLDS["strong"] >= 5.0
        assert HEADCOUNT_THRESHOLDS["neutral"]["min"] == -5.0
        assert HEADCOUNT_THRESHOLDS["neutral"]["max"] == 5.0
        assert HEADCOUNT_THRESHOLDS["reasonably_weak"]["min"] == -10.0
        assert HEADCOUNT_THRESHOLDS["reasonably_weak"]["max"] == -5.0
        assert HEADCOUNT_THRESHOLDS["weak"]["min"] == -20.0
        assert HEADCOUNT_THRESHOLDS["weak"]["max"] == -10.0
        assert HEADCOUNT_THRESHOLDS["collapsing"] <= -20.0

    def test_job_posting_thresholds_structure(self):
        """Job posting thresholds should have all badge levels."""
        expected_levels = ["strong", "neutral", "reasonably_weak", "weak", "collapsing"]
        for level in expected_levels:
            assert level in JOB_POSTING_THRESHOLDS

    def test_job_posting_thresholds_values(self):
        """Job posting thresholds should use absolute numbers."""
        assert JOB_POSTING_THRESHOLDS["strong"] >= 10
        assert JOB_POSTING_THRESHOLDS["neutral"]["min"] == -10
        assert JOB_POSTING_THRESHOLDS["neutral"]["max"] == 10
        assert JOB_POSTING_THRESHOLDS["reasonably_weak"]["min"] == -20
        assert JOB_POSTING_THRESHOLDS["reasonably_weak"]["max"] == -10
        assert JOB_POSTING_THRESHOLDS["weak"]["min"] == -40
        assert JOB_POSTING_THRESHOLDS["weak"]["max"] == -20
        assert JOB_POSTING_THRESHOLDS["collapsing"] <= -40
