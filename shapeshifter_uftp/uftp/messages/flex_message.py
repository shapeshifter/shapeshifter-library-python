from dataclasses import dataclass, field
from typing import List, Optional

from xsdata.models.datatype import XmlDate, XmlDuration

from ..defaults import DEFAULT_TIME_ZONE
from .payload_message import PayloadMessage, PayloadMessageResponse


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
