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
class FlexOrderISP:
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
        name = "FlexOrderISP"

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
class FlexOrderResponse(PayloadMessageResponse):
    flex_order_message_id: str = field(
        metadata={
            "name": "FlexOrderMessageID",
            "type": "Attribute",
            "required": True,
            "pattern": r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}",
        }
    )

@dataclass(kw_only=True)
class FlexOrder(FlexMessage):
    """
    :ivar isp:
    :ivar flex_offer_message_id: MessageID of the FlexOffer message this
        order is based on.
    :ivar contract_id: Reference to the concerning bilateral contract,
        if applicable.
    :ivar d_prognosis_message_id: MessageID of the D-Prognosis this
        request is based on, if it has been agreed that the baseline is
        based on D-prognoses.
    :ivar baseline_reference: Identification of the baseline prognosis,
        if another baseline methodology is used than based on
        D-prognoses
    :ivar price: The price for the flexibility ordered. Usually, the
        price should match the price of the related FlexOffer.
    :ivar currency: ISO 4217 code indicating the currency that applies
        to the price of the FlexOffer.
    :ivar order_reference: Order number assigned by the DSO originating
        the FlexOrder. To be stored by the AGR and used in the
        settlement phase.
    :ivar option_reference: The OptionReference from the OfferOption
        chosen from the FlexOffer.
    :ivar activation_factor: The activation factor for this OfferOption.
        The ActivationFactor must be greater than or equal to the
        MinActivationFactor in the OfferOption chosen from the
        FlexOffer.
    """
    isps: List[FlexOrderISP] = field(
        default_factory=list,
        metadata={
            "name": "ISP",
            "type": "Element",
            "min_occurs": 1,
        }
    )
    flex_offer_message_id: str = field(
        metadata={
            "name": "FlexOfferMessageID",
            "type": "Attribute",
            "required": True,
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
    price: Decimal = field(
        metadata={
            "name": "Price",
            "type": "Attribute",
            "required": True,
            "fraction_digits": 4,
        }
    )
    currency: str = field(
        metadata={
            "name": "Currency",
            "type": "Attribute",
            "required": True,
            "pattern": r"[A-Z]{3}",
        }
    )
    order_reference: str = field(
        metadata={
            "name": "OrderReference",
            "type": "Attribute",
            "required": True,
        }
    )
    option_reference: Optional[str] = field(
        default=None,
        metadata={
            "name": "OptionReference",
            "type": "Attribute",
        }
    )
    activation_factor: Decimal = field(
        default=Decimal("1.00"),
        metadata={
            "name": "ActivationFactor",
            "type": "Attribute",
            "min_inclusive": Decimal("0.01"),
            "max_inclusive": Decimal("1.00"),
            "fraction_digits": 2,
        }
    )

    def __post_init__(self):
        validate_list("isps", self.isps, FlexOrderISP, 1)
        self.price = validate_decimal("price", self.price, 4)
        self.activation_factor = validate_decimal(
            "activation_factor", self.activation_factor, 2
        )
