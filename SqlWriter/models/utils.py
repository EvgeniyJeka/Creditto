import math
from decimal import *


class Calculator:

    @staticmethod
    def precise(input):
        """
        This method can be used to convert a value that would considered invalid in our system , for example -
        float with more than 8 tail digits  to a valid value.
        The value is rounded down to 8 tail digits and converted to decimal.
        :param input: float
        :return Decimal
        """

        num_to_line = str(input)

        cnt = 0
        pos = 0

        for _char in num_to_line:
            if _char == '.':
                pos = cnt
            cnt += 1

        num_8_digits = num_to_line[:pos + 9]

        result = Decimal(num_8_digits)

        # Rounding - handling special case when 9'th digit after the decimal point greater than 5
        if len(num_to_line) > pos + 9:
            if int(num_to_line[pos + 9]) >= 5:
                result += Decimal(0.00000001)
                result = Decimal(str(result)[:pos + 9])

        return result