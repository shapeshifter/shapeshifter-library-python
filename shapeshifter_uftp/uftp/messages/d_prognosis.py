from dataclasses import dataclass, field
from typing import List, Optional

from xsdata.models.datatype import XmlDate, XmlDuration

from ..defaults import DEFAULT_TIME_ZONE
from ..enums import RedispatchBy
from ..validations import validate_list
from .flex_message import FlexMessage
from .payload_message import PayloadMessage, PayloadMessageResponse


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
