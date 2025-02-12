from dataclasses import dataclass, field
from typing import List, Optional

from xsdata.models.datatype import XmlDate, XmlDuration

from ..defaults import DEFAULT_TIME_ZONE
from ..enums import RedispatchBy
from ..validations import validate_list
from .flex_message import FlexMessage
from .payload_message import PayloadMessage, PayloadMessageResponse


@dataclass(kw_only=True)
class DsoPortfolioUpdateConnection:
    """
    A connection that the DSO wants the CRO to update.

    :ivar entity_address: EntityAddress of the Connection.
    :ivar start_period: The first Period that the Connection is part of
        this CongestionPoint.
    :ivar end_period: The last Period that the Connection is part of
        this CongestionPoint.
    """
    class Meta:
        name = "DSOPortfolioUpdateConnection"

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
class DsoPortfolioUpdateCongestionPoint:
    """
    A congestion point that the DSO wants the CRO to update.

    :ivar connection:
    :ivar entity_address: EntityAddress of the Connection.
    :ivar start_period: The first Period that the Connection is part of
        this CongestionPoint.
    :ivar end_period: The last Period that the Connection is part of
        this CongestionPoint.
    :ivar mutex_offers_supported: Indicates whether the DSO accepts
        mutual exclusive FlexOffers on this CongestionPoint.
    :ivar day_ahead_redispatch_by: Indicates which party is responsible
        for day-ahead redispatch.
    :ivar intraday_redispatch_by: Indicates which party is responsible
        for intraday ahead redispatch, AGR or DSO. If not specified,
        there will be no intraday trading on this CongestionPoint.
    """
    class Meta:
        name = "DSOPortfolioUpdateCongestionPoint"

    connections: List[DsoPortfolioUpdateConnection] = field(
        default_factory=list,
        metadata={
            "name": "Connection",
            "type": "Element",
            "min_occurs": 1,
        }
    )
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
    mutex_offers_supported: bool = field(
        metadata={
            "name": "MutexOffersSupported",
            "type": "Attribute",
            "required": True,
        }
    )
    day_ahead_redispatch_by: RedispatchBy = field(
        metadata={
            "name": "DayAheadRedispatchBy",
            "type": "Attribute",
            "required": True,
        }
    )
    intraday_redispatch_by: Optional[RedispatchBy] = field(
        default=None,
        metadata={
            "name": "IntradayRedispatchBy",
            "type": "Attribute",
        }
    )

    def __post_init__(self):
        validate_list('connections', self.connections, DsoPortfolioUpdateConnection, 1)


@dataclass(kw_only=True)
class DsoPortfolioUpdateResponse(PayloadMessageResponse):
    class Meta:
        name = "DSOPortfolioUpdateResponse"

    dso_portfolio_update_message_id: str = field(
        metadata={
            "name": "DSOPortfolioUpdateResponseMessageID",
            "type": "Attribute",
            "required": True,
            "pattern": r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}",
        }
    )


@dataclass(kw_only=True)
class DsoPortfolioUpdate(PayloadMessage):
    """
    :ivar congestion_point:
    :ivar time_zone: Time zone ID (as per the IANA time zone database,
        http://www.iana.org/time-zones, for example: Europe/Amsterdam)
        indicating the UTC offset that applies to the Period referenced
        in this message. Although the time zone is a market-wide fixed
        value, making this assumption explicit in each message is
        important for validation purposes, allowing implementations to
        reject messages with an errant UTC offset.
    """
    class Meta:
        name = "DSOPortfolioUpdate"

    congestion_points: List[DsoPortfolioUpdateCongestionPoint] = field(
        default_factory=list,
        metadata={
            "name": "CongestionPoint",
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
        validate_list('congestion_points', self.congestion_points, DsoPortfolioUpdateCongestionPoint, 1)
