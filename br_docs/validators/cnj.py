import re

from pydantic_core import PydanticCustomError

from br_docs.validators.types.format import ValuesRegex


class CNJv(ValuesRegex):
    """
    CNJ (Conselho Nacional de Justiça) validator
    Format: NNNNNNN-DD.AAAA.J.TR.OOOO
    Where:
        - NNNNNNN: 7-digit sequential process number
        - DD: 2 check digits
        - AAAA: 4-digit registration year
        - J: 1-digit judicial segment (1-9)
        - TR: 2-digit tribunal code
        - OOOO: 4-digit origin code

    Check digit calculation uses modulo 97 algorithm:
    DD = 98 - ((OOOO + AAAA + J + TR + NNNNNNN) mod 97)

    Note: Unlike other Brazilian documents, CNJ check digits are in the middle
    of the number, not at the end.
    """
    Patterns = (
        re.compile(r"^\d{20}$"),  # Without formatting: 12345678901234567890
        re.compile(r"^\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}$"),  # Formatted: 1234567-89.0123.4.56.7890
    )

    def __call__(self, value: str) -> str:
        self.check_format(value)
        self.validate(value)
        return value

    def validate(self, value: str):
        """
        Validate CNJ number by checking the check digits.

        Args:
            value: CNJ number (formatted or unformatted)

        Raises:
            PydanticCustomError: If check digits are invalid
        """
        # Extract all digits from the value
        digits = list(map(int, re.findall(r"\d", value)))

        # Extract components from the 20 digits
        # Format: NNNNNNN (7) + DD (2) + AAAA (4) + J (1) + TR (2) + OOOO (4)
        sequential = digits[0:7]      # NNNNNNN
        check_digits = digits[7:9]    # DD (these are what we need to verify)
        year = digits[9:13]           # AAAA
        segment = [digits[13]]        # J
        tribunal = digits[14:16]      # TR
        origin = digits[16:20]        # OOOO

        # Calculate expected check digits
        calculated_check = self.calculate_check_digit(
            sequential, year, segment, tribunal, origin
        )

        # Compare calculated vs actual
        actual_check = check_digits[0] * 10 + check_digits[1]

        if calculated_check != actual_check:
            raise PydanticCustomError(
                'invalid',
                'Invalid CNJ check digits'
            )

    @staticmethod
    def calculate_check_digit(
        sequential: list[int],
        year: list[int],
        segment: list[int],
        tribunal: list[int],
        origin: list[int]
    ) -> int:
        """
        Calculate CNJ check digit using modulo 97 algorithm.

        The calculation follows CNJ Resolution 65/2008:
        1. Organize digits as: OOOO (origin) + AA (year last 2 digits) + J (segment) + TR (tribunal) + NNNNNNN (sequential)
        2. Calculate: 98 - (number mod 97)
        3. Result is the 2-digit check digit

        Args:
            sequential: 7-digit sequential process number
            year: 4-digit registration year (only last 2 digits are used)
            segment: 1-digit judicial segment
            tribunal: 2-digit tribunal code
            origin: 4-digit origin code

        Returns:
            Two-digit check digit (0-97)
        """
        # Build number for calculation: OOOO + AA (last 2 of year) + J + TR + NNNNNNN
        # Use only last 2 digits of year
        year_2d = year[2:4]
        calc_number = origin + year_2d + segment + tribunal + sequential

        # Convert to integer
        number = int(''.join(map(str, calc_number)))

        # Calculate check digit: 98 - (number mod 97)
        check_digit = 98 - (number % 97)

        return check_digit
