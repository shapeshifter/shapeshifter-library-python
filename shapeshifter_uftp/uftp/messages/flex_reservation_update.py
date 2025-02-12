from dataclasses import dataclass, field
from typing import List, Optional

from xsdata.models.datatype import XmlDate, XmlDuration

from ..defaults import DEFAULT_TIME_ZONE
from ..enums import RedispatchBy
from ..validations import validate_list
from .flex_message import FlexMessage
from .payload_message import PayloadMessage, PayloadMessageResponse


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
