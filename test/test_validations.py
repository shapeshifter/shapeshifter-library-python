from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from uuid import uuid4

import pytest
from xsdata.models.datatype import XmlDate, XmlDuration

from shapeshifter_uftp.uftp.messages import (
    FlexOffer,
    FlexOfferOption,
    FlexOfferOptionISP,
    FlexOrder,
    FlexOrderISP,
)
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


def test_not_unsolicited_flex_order_without_request_id():
    with pytest.raises(TypeError):
        FlexOrder(
            isps=[FlexOrderISP(
                power=123,
                start=1
            )],
            isp_duration=XmlDuration("PT15M"),
            period=XmlDate(2023,1,1),
            congestion_point="ean.123456789012345678",
            price=Decimal("0.0"),
            currency="EUR",
            order_reference=str(uuid4())
        )

def test_not_unsollicited_flex_offer_without_request_id():
    with pytest.raises(TypeError):
        FlexOffer(
            isp_duration=XmlDuration("PT15M"),
            period=XmlDate(2023,1,1),
            congestion_point="ean.123456789012345678",
            expiration_date_time=datetime(2023,1,1,0,0,0, tzinfo=timezone.utc).isoformat(),
            offer_options=[
                FlexOfferOption(
                    option_reference=str(uuid4()),
                    price=Decimal("0.0"),
                    isps=[
                        FlexOfferOptionISP(
                            power=1,
                            start=1,
                            duration=1
                        )
                    ]
                )
            ],
        )
