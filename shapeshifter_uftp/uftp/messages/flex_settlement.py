from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional

from xsdata.models.datatype import XmlDate, XmlDuration

from ..defaults import DEFAULT_TIME_ZONE
from ..enums import AcceptedDisputed, RedispatchBy
from ..validations import validate_decimal, validate_list
from .flex_message import FlexMessage
from .payload_message import PayloadMessage, PayloadMessageResponse


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
