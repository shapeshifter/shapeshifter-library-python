from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional
from xsdata.models.datatype import XmlDate, XmlDuration
from .common import (
    AcceptedDisputed,
    AvailableRequested,
    PayloadMessageResponse,
    PayloadMessage,
)
from .validations import validate_decimal, validate_list
from .defaults import DEFAULT_TIME_ZONE


# pylint: disable=missing-class-docstring,duplicate-code,too-many-lines


@dataclass(kw_only=True)
class ContractSettlementISP:
    """
    :ivar start: Number of the first ISPs this element refers to. The
        first ISP of a day has number 1.
    :ivar duration: The number of the ISPs this element represents.
        Optional, default value is 1.
    :ivar reserved_power: Amount of flex power that has been reserved
        (and not released using a FlexReservationUpdate message).
    :ivar requested_power: Amount of flex power that has been both
        reserved in advance and has been requested using a FlexRequest
        (i.e. the lowest amount of flex power for this ISP). If there
        was no FlexRequest, this field is omitted.
    :ivar available_power: Amount of flex power that is considered
        available based on the FlexRequest in question. In case
        RequestedPower=0, AvailablePower is defined so that the offered
        power is allowed to be between 0 and AvailablePower in terms of
        compliancy (see Appendix 'Rationale for information exchange in
        flexibility request' for details). In case RequestedPower ≠0,
        AvailablePower is defined so that the offered power is allowed
        to exceed the amount of requested power up to AvailablePower. If
        this is relevant for settlement, the DSO can include this field.
    :ivar offered_power: Amount of flex power that has been reserved in
        advance, requested using a FlexRequest and covered in an offer
        from the AGR. If there was no offer, this field is omitted. If
        there were multiple offers, only the one is considered that is
        most compliant .
    :ivar ordered_power: Amount of flex power that has been ordered
        using a FlexOrder message that was based on a FlexOffer, both
        linked to this contract. If there was no order, this field is
        omitted.
    """
    class Meta:
        name = "ContractSettlementISP"

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
    reserved_power: int = field(
        metadata={
            "name": "ReservedPower",
            "type": "Attribute",
            "required": True,
        }
    )
    requested_power: Optional[int] = field(
        default=None,
        metadata={
            "name": "RequestedPower",
            "type": "Attribute",
        }
    )
    available_power: Optional[int] = field(
        default=None,
        metadata={
            "name": "AvailablePower",
            "type": "Attribute",
        }
    )
    offered_power: Optional[int] = field(
        default=None,
        metadata={
            "name": "OfferedPower",
            "type": "Attribute",
        }
    )
    ordered_power: Optional[int] = field(
        default=None,
        metadata={
            "name": "OrderedPower",
            "type": "Attribute",
        }
    )


@dataclass(kw_only=True)
class DPrognosisISP:
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
        name = "D-PrognosisISP"

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
class FlexOrderSettlementISP:
    """
    :ivar start: Number of the first ISPs this element refers to. The
        first ISP of a day has number 1.
    :ivar duration: The number of the ISPs this element represents.
        Optional, default value is 1.
    :ivar baseline_power: Power originally forecast (as per the
        referenced baseline) for this ISP in Watts.
    :ivar ordered_flex_power: Amount of flex power ordered (as per the
        referenced FlexOrder message) for this ISP in Watts.
    :ivar actual_power: Actual amount of power for this ISP in Watts, as
        measured/determined by the DSO and allocated to the AGR.
    :ivar delivered_flex_power: Actual amount of flex power delivered
        for this ISP in Watts, as determined by the DSO.
    :ivar power_deficiency: Amount of flex power sold but not delivered
        for this ISP in Watts, as determined by the DSO.
    """
    class Meta:
        name = "FlexOrderSettlementISP"

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
    baseline_power: int = field(
        metadata={
            "name": "BaselinePower",
            "type": "Attribute",
            "required": True,
        }
    )
    ordered_flex_power: int = field(
        metadata={
            "name": "OrderedFlexPower",
            "type": "Attribute",
            "required": True,
        }
    )
    actual_power: int = field(
        metadata={
            "name": "ActualPower",
            "type": "Attribute",
            "required": True,
        }
    )
    delivered_flex_power: int = field(
        metadata={
            "name": "DeliveredFlexPower",
            "type": "Attribute",
            "required": True,
        }
    )
    power_deficiency: int = field(
        default=0,
        metadata={
            "name": "PowerDeficiency",
            "type": "Attribute",
        }
    )


@dataclass(kw_only=True)
class FlexOrderStatus:
    flex_order_message_id: str = field(
        metadata={
            "name": "FlexOrderMessageID",
            "type": "Attribute",
            "required": True,
            "pattern": r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}",
        }
    )
    is_validated: bool = field(
        metadata={
            "name": "IsValidated",
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass(kw_only=True)
class FlexReservationUpdateISP:
    """
    :ivar power: Remaining reserved power specified for this ISP in
        Watts.
    :ivar start: Number of the first ISPs this element refers to. The
        first ISP of a day has number 1.
    :ivar duration: The number of the ISPs this element represents.
        Optional, default value is 1.
    """
    class Meta:
        name = "FlexReservationUpdateISP"

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
class ContractSettlementPeriod:
    """
    :ivar isp:
    :ivar period: Period the being settled.
    """
    isps: List[ContractSettlementISP] = field(
        default_factory=list,
        metadata={
            "name": "ISP",
            "type": "Element",
            "min_occurs": 1,
        }
    )
    period: XmlDate = field(
        metadata={
            "name": "Period",
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass(kw_only=True)
class DPrognosisResponse(PayloadMessageResponse):
    class Meta:
        name = "D-PrognosisResponse"

    d_prognosis_message_id: str = field(
        metadata={
            "name": "D-PrognosisMessageID",
            "type": "Attribute",
            "required": True,
            "pattern": r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}",
        }
    )

    flex_order_statuses: List[FlexOrderStatus] = field(
        default_factory=list,
        metadata={
            "name": "FlexOrderStatus",
            "type": "Element",
        }
    )


@dataclass(kw_only=True)
class FlexMessage(PayloadMessage):
    """
    :ivar isp_duration: ISO 8601 time interval (minutes only, for
        example PT15M) indicating the duration of the ISPs referenced in
        this message. Although the ISP length is a market-wide fixed
        value, making this assumption explicit in each message is
        important for validation purposes, allowing implementations to
        reject messages with an errant ISP duration.
    :ivar time_zone: Time zone ID (as per the IANA time zone database,
        http://www.iana.org/time-zones, for example: Europe/Amsterdam)
        indicating the UTC offset that applies to the Period referenced
        in this message. Although the time zone is a market-wide fixed
        value, making this assumption explicit in each message is
        important for validation purposes, allowing implementations to
        reject messages with an errant UTC offset.
    :ivar period: Day (in yyyy-mm-dd format) the ISPs referenced in this
        Flex* message belong to.
    :ivar congestion_point: Entity Address of the Congestion Point this
        D-Prognosis applies to.
    """
    isp_duration: XmlDuration = field(
        metadata={
            "name": "ISP-Duration",
            "type": "Attribute",
            "required": True,
        }
    )
    time_zone: str = field(
        default=DEFAULT_TIME_ZONE,
        metadata={
            "name": "TimeZone",
            "type": "Attribute",
            "required": True,
            "pattern": r"(Africa|America|Australia|Europe|Pacific)/[a-zA-Z0-9_/]{3,}",
        }
    )
    period: XmlDate = field(
        metadata={
            "name": "Period",
            "type": "Attribute",
            "required": True,
        }
    )
    congestion_point: str = field(
        metadata={
            "name": "CongestionPoint",
            "type": "Attribute",
            "required": True,
            "pattern": r"(ea1\.[0-9]{4}-[0-9]{2}\..{1,244}:.{1,244}|ean\.[0-9]{12,34})",
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
class FlexOfferRevocationResponse(PayloadMessageResponse):
    flex_offer_revocation_message_id: str = field(
        metadata={
            "name": "FlexOfferRevocationMessageID",
            "type": "Attribute",
            "required": True,
            "pattern": r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}",
        }
    )


@dataclass(kw_only=True)
class FlexOfferRevocation(PayloadMessage):
    """
    :ivar flex_offer_message_id: MessageID of the FlexOffer message that
        is being revoked: this FlexOffer must have been accepted
        previously.
    """
    flex_offer_message_id: str = field(
        metadata={
            "name": "FlexOfferMessageID",
            "type": "Attribute",
            "required": True,
            "pattern": r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}",
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
class FlexOrderSettlementStatus:
    """
    :ivar order_reference: Order reference assigned by the DSO when
        originating the FlexOrder.
    :ivar disposition: Indication whether the AGR accepts the order
        settlement details provided by the DSO (and will invoice
        accordingly), or disputes these details.
    :ivar dispute_reason: In case the order settlement was disputed,
        this attribute must contain a human-readable description of the
        reason.
    """
    order_reference: Optional[str] = field(
        default=None,
        metadata={
            "name": "OrderReference",
            "type": "Attribute",
        }
    )
    disposition: AcceptedDisputed = field(
        metadata={
            "name": "Disposition",
            "type": "Attribute",
            "required": True,
        }
    )
    dispute_reason: Optional[str] = field(
        default=None,
        metadata={
            "name": "DisputeReason",
            "type": "Attribute",
        }
    )


@dataclass(kw_only=True)
class FlexOrderSettlement:
    """
    :ivar isp:
    :ivar order_reference: Order reference assigned by the DSO when
        originating the FlexOrder.
    :ivar period:
    :ivar contract_id: Reference to the concerning bilateral contract,
        if it is linked to it
    :ivar d_prognosis_message_id: MessageID of the Prognosis message
        (more specifically: the D-Prognosis) the FlexOrder is based on,
        if it has been agreed that the baseline is based on D-prognoses.
    :ivar baseline_reference: Identification of the baseline prognosis,
        if another baseline methodology is used than based on
        D-prognoses.
    :ivar congestion_point: Entity Address of the Congestion Point the
        FlexOrder applies to.
    :ivar price: The price accepted for supplying the ordered amount of
        flexibility as per the referenced FlexOrder messages.
    :ivar penalty: Penalty due a non-zero PowerDeficiency
    :ivar net_settlement: Net settlement amount for this Period: Price
        minus Penalty.
    """
    isps: List[FlexOrderSettlementISP] = field(
        default_factory=list,
        metadata={
            "name": "ISP",
            "type": "Element",
            "min_occurs": 1,
        }
    )
    order_reference: Optional[str] = field(
        default=None,
        metadata={
            "name": "OrderReference",
            "type": "Attribute",
        }
    )
    period: XmlDate = field(
        metadata={
            "name": "Period",
            "type": "Attribute",
            "required": True,
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
    congestion_point: str = field(
        metadata={
            "name": "CongestionPoint",
            "type": "Attribute",
            "required": True,
            "pattern": r"(ea1\.[0-9]{4}-[0-9]{2}\..{1,244}:.{1,244}|ean\.[0-9]{12,34})",
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
    penalty: Decimal = field(
        default=Decimal("0"),
        metadata={
            "name": "Penalty",
            "type": "Attribute",
            "fraction_digits": 4,
        }
    )
    net_settlement: Decimal = field(
        metadata={
            "name": "NetSettlement",
            "type": "Attribute",
            "required": True,
            "fraction_digits": 4,
        }
    )

    def __post_init__(self):
        validate_list('isps', self.isps, FlexOrderSettlementISP, 1)
        self.price = validate_decimal('price', self.price, 4)
        self.penalty = validate_decimal('penalty', self.penalty, 4)
        self.net_settlement = validate_decimal('net_settlement', self.net_settlement, 4)


@dataclass(kw_only=True)
class FlexRequestISP:
    """
    :ivar disposition:
    :ivar min_power: Power specified for this ISP in Watts. Also see the
        important notes about the sign of this attribute in the main
        documentation entry for the ISP element.
    :ivar max_power: Power specified for this ISP in Watts. Also see the
        important notes about the sign of this attribute in the main
        documentation entry for the ISP element.
    :ivar start: Number of the first ISPs this element refers to. The
        first ISP of a day has number 1.
    :ivar duration: The number of the ISPs this element represents.
        Optional, default value is 1.
    """
    class Meta:
        name = "FlexRequestISP"

    disposition: Optional[AvailableRequested] = field(
        default=None,
        metadata={
            "name": "Disposition",
            "type": "Attribute",
        }
    )
    min_power: int = field(
        metadata={
            "name": "MinPower",
            "type": "Attribute",
            "required": True,
        }
    )
    max_power: int = field(
        metadata={
            "name": "MaxPower",
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
class FlexRequestResponse(PayloadMessageResponse):

    flex_request_message_id: str = field(
        metadata={
            "name": "FlexRequestMessageID",
            "type": "Attribute",
            "required": True,
            "pattern": r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}",
        }
    )


@dataclass(kw_only=True)
class FlexReservationUpdateResponse(PayloadMessageResponse):

    flex_reservation_update_message_id: str = field(
        metadata={
            "name": "FlexReservationUpdateMessageID",
            "type": "Attribute",
            "required": True,
            "pattern": r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}",
        }
    )


@dataclass(kw_only=True)
class ContractSettlement:
    """
    :ivar period:
    :ivar contract_id: Reference to the concerning bilateral contract.
    """
    periods: List[ContractSettlementPeriod] = field(
        default_factory=list,
        metadata={
            "name": "Period",
            "type": "Element",
            "min_occurs": 1,
        }
    )
    contract_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "ContractID",
            "type": "Attribute",
        }
    )

    def __post_init__(self):
        validate_list('periods', self.periods, ContractSettlementPeriod, 1)


@dataclass(kw_only=True)
class DPrognosis(FlexMessage):
    """
    :ivar isp:
    :ivar revision: Revision of this message. A sequence number that
        must be incremented each time a new revision of a prognosis is
        sent. The combination of SenderDomain and PrognosisSequence
        should be unique
    """
    class Meta:
        name = "D-Prognosis"

    isps: List[DPrognosisISP] = field(
        default_factory=list,
        metadata={
            "name": "ISP",
            "type": "Element",
            "min_occurs": 1,
        }
    )
    revision: int = field(
        metadata={
            "name": "Revision",
            "type": "Attribute",
            "required": True,
        }
    )

    def __post_init__(self):
        validate_list('isps', self.isps, DPrognosisISP, 1)


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

@dataclass(kw_only=True)
class FlexRequest(FlexMessage):
    """
    :ivar isp:
    :ivar revision: Revision of this message, a sequence number that
        must be incremented each time a new revision of a FlexRequest
        message is sent.
    :ivar expiration_date_time: Date and time, including the time zone
        (ISO 8601 formatted as per http://www.w3.org/TR/NOTE-datetime)
        until which the FlexRequest message is valid.
    :ivar contract_id: Reference to the concerning contract, if
        applicable. The contract may be either bilateral or commoditized
        market contract. Each contract may specify multiple service-
        types.
    :ivar service_type: Service type for this request, the service type
        determines response characteristics such as latency or asset
        participation type.
    """
    isps: List[FlexRequestISP] = field(
        default_factory=list,
        metadata={
            "name": "ISP",
            "type": "Element",
            "min_occurs": 1,
        }
    )
    revision: int = field(
        metadata={
            "name": "Revision",
            "type": "Attribute",
            "required": True,
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
    contract_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "ContractID",
            "type": "Attribute",
        }
    )
    service_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "ServiceType",
            "type": "Attribute",
        }
    )

    def __post_init__(self):
        validate_list('isps', self.isps, FlexRequestISP, 1)


@dataclass(kw_only=True)
class FlexReservationUpdate(FlexMessage):
    """
    :ivar isp:
    :ivar contract_id: Reference to the bilateral contract in question.
    :ivar reference: Message reference, assigned by the DSO originating
        the FlexReservationUpdate.
    """
    isps: List[FlexReservationUpdateISP] = field(
        default_factory=list,
        metadata={
            "name": "ISP",
            "type": "Element",
            "min_occurs": 1,
        }
    )
    contract_id: str = field(
        metadata={
            "name": "ContractID",
            "type": "Attribute",
            "required": True,
        }
    )
    reference: str = field(
        metadata={
            "name": "Reference",
            "type": "Attribute",
            "required": True,
        }
    )

    def __post_init__(self):
        validate_list('isps', self.isps, FlexReservationUpdateISP, 1)


@dataclass(kw_only=True)
class FlexSettlementResponse(PayloadMessageResponse):
    flex_settlement_message_id: str = field(
        metadata={
            "name": "FlexSettlementMessageID",
            "type": "Attribute",
            "required": True,
            "pattern": r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}",
        }
    )

    flex_order_settlement_statuses: List[FlexOrderSettlementStatus] = field(
        default_factory=list,
        metadata={
            "name": "FlexOrderSettlementStatus",
            "type": "Element",
            "min_occurs": 1,
        }
    )

    def __post_init__(self):
        validate_list(
            "flex_order_settlement_statuses",
            self.flex_order_settlement_statuses,
            FlexOrderSettlementStatus,
            1,
        )


@dataclass(kw_only=True)
class FlexSettlement(PayloadMessageResponse):
    """
    :ivar flex_order_settlement:
    :ivar contract_settlement:
    :ivar period_start: First Period of the settlement period this
        message applies to.
    :ivar period_end: Last Period of the settlement period this message
        applies to.
    :ivar currency: ISO 4217 code indicating the currency that applies
        to all amounts (flex price, penalty and net settlement) in this
        message.
    """
    flex_order_settlements: List[FlexOrderSettlement] = field(
        default_factory=list,
        metadata={
            "name": "FlexOrderSettlement",
            "type": "Element",
            "min_occurs": 1,
        }
    )
    contract_settlements: List[ContractSettlement] = field(
        default_factory=list,
        metadata={
            "name": "ContractSettlement",
            "type": "Element",
            "min_occurs": 1,
        }
    )
    period_start: XmlDate = field(
        metadata={
            "name": "PeriodStart",
            "type": "Attribute",
            "required": True,
        }
    )
    period_end: XmlDate = field(
        metadata={
            "name": "PeriodEnd",
            "type": "Attribute",
            "required": True,
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

    def __post_init__(self):
        validate_list(
            "flex_order_settlements", self.flex_order_settlements, FlexOrderSettlement, 1
        )
        validate_list(
            "contract_settlements", self.contract_settlements, ContractSettlement, 1
        )
