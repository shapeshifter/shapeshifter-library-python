from dataclasses import dataclass, field
from typing import List, Optional

from xsdata.models.datatype import XmlDate, XmlDuration

from ..defaults import DEFAULT_TIME_ZONE
from ..enums import AvailableRequested
from ..validations import validate_list
from .flex_message import FlexMessage
from .payload_message import PayloadMessage, PayloadMessageResponse


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
