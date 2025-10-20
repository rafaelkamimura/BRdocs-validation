"""
Comprehensive test suite for CNJ (Conselho Nacional de Justiça) validator
"""
import pytest
from pydantic import BaseModel, ValidationError

from br_docs import CNJ


class TestCNJFormat:
    """Test CNJ format validation"""

    def test_formatted_cnj_valid(self):
        """Test valid CNJ with formatting (NNNNNNN-DD.AAAA.J.TR.OOOO)"""
        class Model(BaseModel):
            cnj: CNJ

        # Valid formatted CNJ (with correct check digits)
        valid_cnjs = [
            "0000001-19.2016.8.26.0100",
            "0000002-18.2016.8.26.0100",
            "0123456-70.2019.4.01.3800",
            "1234567-07.2018.1.00.0000",
        ]
        for cnj in valid_cnjs:
            model = Model(cnj=cnj)
            assert model.cnj == cnj

    def test_unformatted_cnj_valid(self):
        """Test valid CNJ without formatting (20 digits)"""
        class Model(BaseModel):
            cnj: CNJ

        # Valid unformatted CNJ (with correct check digits)
        valid_cnjs = [
            "00000011920168260100",
            "00000021820168260100",
            "01234567020194013800",
            "12345670720181000000",
        ]
        for cnj in valid_cnjs:
            model = Model(cnj=cnj)
            assert model.cnj == cnj

    def test_invalid_format(self):
        """Test CNJ with invalid format"""
        class Model(BaseModel):
            cnj: CNJ

        invalid_formats = [
            "123456-78.2019.4.01.3800",      # Too short (6 digits instead of 7)
            "00000001-02.2016.8.26.0100",     # Too long (8 digits instead of 7)
            "0000001-02.2016.8.26.01000",     # Origin too long
            "0000001-02.2016.10.26.0100",     # Segment too long
            "0000001-2.2016.8.26.0100",       # Check digit too short
            "000001-02.2016.8.26.0100",       # Sequential too short
        ]
        for cnj in invalid_formats:
            with pytest.raises(ValidationError):
                Model(cnj=cnj)


class TestCNJCheckDigits:
    """Test CNJ check digit validation"""

    def test_valid_check_digits(self):
        """Test CNJ with correct check digits"""
        class Model(BaseModel):
            cnj: CNJ

        valid_cnjs = [
            "0000001-19.2016.8.26.0100",  # Check: 19
            "0000002-18.2016.8.26.0100",  # Check: 18
            "0000003-17.2016.8.26.0100",  # Check: 17
            "0000001-06.2020.5.02.0001",  # Check: 06
        ]
        for cnj in valid_cnjs:
            model = Model(cnj=cnj)
            assert model.cnj == cnj

    def test_invalid_check_digits(self):
        """Test CNJ with incorrect check digits"""
        class Model(BaseModel):
            cnj: CNJ

        # Same CNJ with wrong check digits
        invalid_cnjs = [
            "0000001-00.2016.8.26.0100",  # Should be 19
            "0000001-20.2016.8.26.0100",  # Should be 19
            "0000002-17.2016.8.26.0100",  # Should be 18
            "0000003-16.2016.8.26.0100",  # Should be 17
            "0000001-07.2020.5.02.0001",  # Should be 06
        ]
        for cnj in invalid_cnjs:
            with pytest.raises(ValidationError):
                Model(cnj=cnj)


class TestCNJComponents:
    """Test different CNJ components"""

    def test_different_years(self):
        """Test CNJ with different years"""
        class Model(BaseModel):
            cnj: CNJ

        valid_cnjs = [
            "0000001-40.2010.5.01.0000",
            "0000001-88.2011.5.01.0000",
            "0000001-39.2012.5.01.0000",
            "0000001-87.2013.5.01.0000",
            "0000001-38.2014.5.01.0000",
            "0000001-86.2015.5.01.0000",
        ]
        for cnj in valid_cnjs:
            model = Model(cnj=cnj)
            assert model.cnj == cnj

    def test_different_segments(self):
        """Test CNJ with different judicial segments (1-9)"""
        class Model(BaseModel):
            cnj: CNJ

        # Different segments
        segments = [
            "1234567-07.2018.1.00.0000",  # Segment 1: STF
            "0000001-06.2020.5.02.0001",  # Segment 5: Labor Justice
            "0000001-09.2023.6.13.0000",  # Segment 6: Military Justice
            "0000001-73.2024.7.20.0000",  # Segment 7: Electoral Justice
            "0000001-19.2016.8.26.0100",  # Segment 8: State Justice
        ]
        for cnj in segments:
            model = Model(cnj=cnj)
            assert model.cnj == cnj

    def test_different_tribunals(self):
        """Test CNJ with different tribunal codes"""
        class Model(BaseModel):
            cnj: CNJ

        tribunals = [
            "0000001-59.2017.3.15.0000",  # TR: 15
            "0000001-06.2020.5.02.0001",  # TR: 02
            "0000001-19.2016.8.26.0100",  # TR: 26 (TJSP)
            "0123456-70.2019.4.01.3800",  # TR: 01
        ]
        for cnj in tribunals:
            model = Model(cnj=cnj)
            assert model.cnj == cnj

    def test_sequential_numbers(self):
        """Test CNJ with different sequential numbers"""
        class Model(BaseModel):
            cnj: CNJ

        sequential = [
            "0000001-19.2016.8.26.0100",
            "0000100-97.2022.8.26.0562",
            "0001000-92.2022.8.26.0224",
            "0010000-84.2022.8.26.0114",
            "0100000-24.2022.8.26.0100",
            "1000000-87.2022.8.26.0100",
            "9999999-40.2020.8.26.0100",
        ]
        for cnj in sequential:
            model = Model(cnj=cnj)
            assert model.cnj == cnj


class TestCNJEdgeCases:
    """Test edge cases for CNJ validation"""

    def test_letters_in_number(self):
        """Test that letters are rejected"""
        class Model(BaseModel):
            cnj: CNJ

        invalid = [
            "ABCDEFG-12.2018.1.00.0000",
            "0000001-AB.2016.8.26.0100",
            "0000001-02.ABCD.8.26.0100",
            "0000001-02.2016.X.26.0100",
            "0000001-02.2016.8.AB.0100",
            "0000001-02.2016.8.26.ABCD",
        ]
        for cnj in invalid:
            with pytest.raises(ValidationError):
                Model(cnj=cnj)

    def test_special_characters(self):
        """Test that only allowed special characters are accepted"""
        class Model(BaseModel):
            cnj: CNJ

        # Valid with correct formatting
        Model(cnj="0000001-19.2016.8.26.0100")

        # Invalid with wrong characters
        invalid = [
            "0000001/02.2016.8.26.0100",
            "0000001-02,2016.8.26.0100",
            "0000001-02.2016-8.26.0100",
            "0000001-02.2016.8-26.0100",
        ]
        for cnj in invalid:
            with pytest.raises(ValidationError):
                Model(cnj=cnj)

    def test_empty_string(self):
        """Test that empty string is rejected"""
        class Model(BaseModel):
            cnj: CNJ

        with pytest.raises(ValidationError):
            Model(cnj="")

    def test_all_zeros_with_correct_check(self):
        """Test CNJ with mostly zeros but correct check digit"""
        class Model(BaseModel):
            cnj: CNJ

        # This should be valid if check digit is correct
        model = Model(cnj="0000001-19.2016.8.26.0100")
        assert model.cnj == "0000001-19.2016.8.26.0100"


class TestCNJPydanticIntegration:
    """Test integration with Pydantic models"""

    def test_in_pydantic_model(self):
        """Test CNJ as part of a larger Pydantic model"""
        class LegalCase(BaseModel):
            process_number: CNJ
            description: str

        case = LegalCase(
            process_number="0000001-19.2016.8.26.0100",
            description="Test case"
        )
        assert case.process_number == "0000001-19.2016.8.26.0100"
        assert case.description == "Test case"

    def test_multiple_cnj_fields(self):
        """Test model with multiple CNJ fields"""
        class RelatedCases(BaseModel):
            main_case: CNJ
            related_case: CNJ

        cases = RelatedCases(
            main_case="0000001-19.2016.8.26.0100",
            related_case="0000002-18.2016.8.26.0100"
        )
        assert cases.main_case == "0000001-19.2016.8.26.0100"
        assert cases.related_case == "0000002-18.2016.8.26.0100"

    def test_optional_cnj(self):
        """Test optional CNJ field"""
        from typing import Optional

        class CaseWithOptional(BaseModel):
            main_case: CNJ
            appeal_case: Optional[CNJ] = None

        # With appeal
        case1 = CaseWithOptional(
            main_case="0000001-19.2016.8.26.0100",
            appeal_case="0000002-18.2016.8.26.0100"
        )
        assert case1.appeal_case == "0000002-18.2016.8.26.0100"

        # Without appeal
        case2 = CaseWithOptional(main_case="0000001-19.2016.8.26.0100")
        assert case2.appeal_case is None
