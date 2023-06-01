import pytest
from decimal import Decimal, InvalidOperation
from shapeshifter_uftp.uftp.validations import validate_decimal, validate_list


@pytest.mark.parametrize(
    "value,decimals,expected_output",
    [
        ("1.0", 4, Decimal("1.0000")),
        ("1", 4, Decimal("1.0000")),
        (1, 4, Decimal("1.0000")),
        (1.0, 4, Decimal("1.0000")),
        (1.00000, 4, Decimal("1.0000")),
        (Decimal("1.0"), 4, Decimal("1.0000")),
    ],
)
def test_validate_decimal(value, decimals, expected_output):
    assert validate_decimal("myvalue", value, decimals) == Decimal("1.0000")


@pytest.mark.parametrize(
    "value,expected_error", [("abc", ValueError), ([123], TypeError)]
)
def test_validate_decimal_errors(value, expected_error):
    with pytest.raises(expected_error):
        validate_decimal("myvalue", value, 4)


@pytest.mark.parametrize('value,obj_type,length,expected_error',
    [
        (None, str, 1, TypeError),
        ([], str, 1, ValueError),
        ([1], str, 1, TypeError),
        (['1'], str, 2, ValueError),
    ]
)
def test_validate_list_errors(value, obj_type, length, expected_error):
    with pytest.raises(expected_error):
        validate_list('mylist', value, obj_type, length)
