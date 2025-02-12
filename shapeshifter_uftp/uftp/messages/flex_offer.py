from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional

from xsdata.models.datatype import XmlDate, XmlDuration

from ..defaults import DEFAULT_TIME_ZONE
from ..enums import RedispatchBy
from ..validations import validate_decimal, validate_list
from .flex_message import FlexMessage
from .payload_message import PayloadMessage, PayloadMessageResponse


@dataclass(kw_only=True)
class FlexOfferOptionISP:
    """
    :ivar power: Power specified for this ISP in Watts. Also see the
        important notes about the sign of this attribute in the main
        documentation entry for the ISP element.
    :ivar start: Number of the first ISPs this element refers to. The
        first ISP of a day has number 1.
    :ivar duration: The number of the ISPs this element represents.
        Optional, default value is 1.
    """
    class Meta:
        name = "FlexOfferOptionISP"

    power: int = field(
        metadata={
            "name": "Power",
            "type": "Attribute",
            "required": True,
        }
    )
    start: int = field(
        metadata={
            "name": "Start",
            "type": "Attribute",
            "required": True,
        }
    )
    duration: int = field(
        default=1,
        metadata={
            "name": "Duration",
            "type": "Attribute",
        }
    )


@dataclass(kw_only=True)
class FlexOfferOption:
    """
    :ivar isp:
    :ivar option_reference: The identification of this option.
    :ivar price: The asking price for the flexibility offered in this
        option.
    :ivar min_activation_factor: The minimal activation factor for this
        OfferOption. An AGR may choose to include MinActivationFactor in
        FlexOffers even if the DSO is not interested in partial
        activation. In that case the DSO will simply use an
        ActivationFactor of 1.00 in every FlexOrder.
    """
    isps: List[FlexOfferOptionISP] = field(
        default_factory=list,
        metadata={
            "name": "ISP",
            "type": "Element",
            "min_occurs": 1,
        }
    )
    option_reference: str = field(
        metadata={
            "name": "OptionReference",
            "type": "Attribute",
            "required": True,
        }
    )
    price: Decimal = field(
        metadata={
            "name": "Price",
            "type": "Attribute",
            "required": True,
            "fraction_digits": 4,
        }
    )
    min_activation_factor: Decimal = field(
        default=Decimal("1.00"),
        metadata={
            "name": "MinActivationFactor",
            "type": "Attribute",
            "min_inclusive": Decimal("0.01"),
            "max_inclusive": Decimal("1.00"),
            "fraction_digits": 2,
        }
    )

    def __post_init__(self):
        validate_list('isps', self.isps, FlexOfferOptionISP, 1)
        self.price = validate_decimal('price', self.price, 4)
        self.min_activation_factor = validate_decimal('min_activation_factor', self.min_activation_factor, 2)


@dataclass(kw_only=True)
class FlexOfferResponse(PayloadMessageResponse):
    flex_offer_message_id: str = field(
        metadata={
            "name": "FlexOfferMessageID",
            "type": "Attribute",
            "required": True,
            "pattern": r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}",
        }
    )


@dataclass(kw_only=True)
class FlexOffer(FlexMessage):
    """
    :ivar offer_option:
    :ivar expiration_date_time: Date and time, including the time zone
        (ISO 8601 formatted as per http://www.w3.org/TR/NOTE-datetime)
        until which the FlexOffer is valid.
    :ivar flex_request_message_id: MessageID of the FlexRequest message
        this request is based on. Mandatory if and only if solicited.
    :ivar contract_id: Reference to the concerning contract, if
        applicable. The contract may be either bilateral or commoditized
        market contract.
    :ivar d_prognosis_message_id: MessageID of the D-Prognosis this
        request is based on, if it has been agreed that the baseline is
        based on D-prognoses.
    :ivar baseline_reference: Identification of the baseline prognosis,
        if another baseline methodology is used than based on
        D-prognoses
    :ivar currency: ISO 4217 code indicating the currency that applies
        to the price of the FlexOffer.
    """
    offer_options: List[FlexOfferOption] = field(
        default_factory=list,
        metadata={
            "name": "OfferOption",
            "type": "Element",
            "min_occurs": 1,
        }
    )
    expiration_date_time: str = field(
        metadata={
            "name": "ExpirationDateTime",
            "type": "Attribute",
            "required": True,
            "pattern": r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{0,9})?([+-]\d{2}:\d{2}|Z)",
        }
    )
    flex_request_message_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "FlexRequestMessageID",
            "type": "Attribute",
            "pattern": r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}",
        }
    )
    contract_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "ContractID",
            "type": "Attribute",
        }
    )
    d_prognosis_message_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "D-PrognosisMessageID",
            "type": "Attribute",
            "pattern": r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}",
        }
    )
    baseline_reference: Optional[str] = field(
        default=None,
        metadata={
            "name": "BaselineReference",
            "type": "Attribute",
        }
    )
    currency: str = field(
        default="EUR",
        metadata={
            "name": "Currency",
            "type": "Attribute",
            "required": True,
            "pattern": r"[A-Z]{3}",
        }
    )

    def __post_init__(self):
        validate_list('offer_options', self.offer_options, FlexOfferOption, 1)
