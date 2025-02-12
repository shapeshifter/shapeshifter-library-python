from dataclasses import dataclass, field
from typing import List, Optional

from xsdata.models.datatype import XmlDate, XmlDuration

from ..defaults import DEFAULT_TIME_ZONE
from ..enums import RedispatchBy
from ..validations import validate_list
from .flex_message import FlexMessage
from .payload_message import PayloadMessage, PayloadMessageResponse


@dataclass(kw_only=True)
class AgrPortfolioUpdateConnection:
    """
    A connection that the AGR want the CRO to update.

    :ivar entity_address: EntityAddress of the Connection entity being
        updated.
    :ivar start_period: The first Period hat the AGR represents the
        prosumer at this Connection.
    :ivar end_period: The last Period that the AGR represents the
        prosumer at this Connection, if applicable.
    """
    class Meta:
        name = "AGRPortfolioUpdateConnection"

    entity_address: str = field(
        metadata={
            "name": "EntityAddress",
            "type": "Attribute",
            "required": True,
            "pattern": r"(ea1\.[0-9]{4}-[0-9]{2}\..{1,244}:.{1,244}|ean\.[0-9]{12,34})",
        }
    )
    start_period: XmlDate = field(
        metadata={
            "name": "StartPeriod",
            "type": "Attribute",
            "required": True,
        }
    )
    end_period: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "EndPeriod",
            "type": "Attribute",
        }
    )


@dataclass(kw_only=True)
class AgrPortfolioUpdateResponse(PayloadMessageResponse):
    class Meta:
        name = "AGRPortfolioUpdateResponse"

    agr_portfolio_update_message_id: str = field(
        metadata={
            "name": "AGRPortfolioUpdateMessageID",
            "type": "Attribute",
            "required": True,
            "pattern": r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}",
        }
    )


@dataclass(kw_only=True)
class AgrPortfolioUpdate(PayloadMessage):
    """
    :ivar connection:
    :ivar time_zone: Time zone ID (as per the IANA time zone database,
        http://www.iana.org/time-zones, for example: Europe/Amsterdam)
        indicating the UTC offset that applies to the Period referenced
        in this message. Although the time zone is a market-wide fixed
        value, making this assumption explicit in each message is
        important for validation purposes, allowing implementations to
        reject messages with an errant UTC offset.
    """
    class Meta:
        name = "AGRPortfolioUpdate"

    connections: List[AgrPortfolioUpdateConnection] = field(
        default_factory=list,
        metadata={
            "name": "Connection",
            "type": "Element",
            "min_occurs": 1,
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

    def __post_init__(self):
        validate_list('connections', self.connections, AgrPortfolioUpdateConnection, 1)
