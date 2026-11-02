import json

import pytest

from core.math_question_generator import binary_arithmetic_table


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        ("1000", "0011", "0101"),
        ("1100", "0011", "1001"),
        ("10101", "00111", "01110"),
    ],
)
def test_binary_subtraction_discards_final_carry(a, b, expected):
    answer, _template = binary_arithmetic_table(a, b, "-")
    result_row = json.loads(answer)["rows"][-1]
    actual = "".join(value for value in result_row[1:] if value.strip())
    assert actual == expected
