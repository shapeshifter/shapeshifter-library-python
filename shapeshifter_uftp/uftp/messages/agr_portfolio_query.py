from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional

from xsdata.models.datatype import XmlDate, XmlDuration

from ..defaults import DEFAULT_TIME_ZONE
from ..enums import RedispatchBy
from ..validations import validate_list
from .flex_message import FlexMessage
from .payload_message import PayloadMessage, PayloadMessageResponse


@dataclass(kw_only=True)
class AgrPortfolioQueryResponseConnection:
    """
    :ivar entity_address: EntityAddress of the Connection.
    """
    class Meta:
        name = "AGRPortfolioQueryResponseConnection"

    entity_address: str = field(
        metadata={
            "name": "EntityAddress",
            "type": "Attribute",
            "required": True,
            "pattern": r"(ea1\.[0-9]{4}-[0-9]{2}\..{1,244}:.{1,244}|ean\.[0-9]{12,34})",
        }
    )

@dataclass(kw_only=True)
class AgrPortfolioQueryResponseCongestionPoint:
    """
    :ivar connection:
    :ivar entity_address: EntityAddress of the CongestionPoint.
    :ivar mutex_offers_supported: Indicates whether the DSO accepts
        mutual exclusive FlexOffers on this CongestionPoint.
    :ivar day_ahead_redispatch_by: Indicates which party is responsible
        for day-ahead redispatch.
    :ivar intraday_redispatch_by: Indicates which party is responsible
        for intraday ahead redispatch, AGR or DSO. If not specified,
        there will be no intraday trading on this CongestionPoint.
    """
    class Meta:
        name = "AGRPortfolioQueryResponseCongestionPoint"

    connections: List[AgrPortfolioQueryResponseConnection] = field(
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
        validate_list('connections', self.connections, AgrPortfolioQueryResponseConnection, 1)





@dataclass(kw_only=True)
class AgrPortfolioQueryResponseDSOPortfolio:
    class Meta:
        name = "AGRPortfolioQueryResponseDSOPortfolio"

    congestion_points: List[AgrPortfolioQueryResponseCongestionPoint] = field(
        default_factory=list,
        metadata={
            "name": "CongestionPoint",
            "type": "Element",
            "min_occurs": 1,
        }
    )
    dso_domain: str = field(
        metadata={
            "name": "DSO-Domain",
            "type": "Attribute",
            "required": True,
            "pattern": r"([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}",
        }
    )

    def __post_init__(self):
        validate_list('congestion_points', self.congestion_points, AgrPortfolioQueryResponseCongestionPoint, 1)


@dataclass(kw_only=True)
class AgrPortfolioQueryResponseDSOView:
    class Meta:
        name = "AGRPortfolioQueryResponseDSOView"

    dso_portfolios: List[AgrPortfolioQueryResponseDSOPortfolio] = field(
        default_factory=list,
        metadata={
            "name": "DSO-Portfolio",
            "type": "Element",
            "min_occurs": 1,
        }
    )
    connections: List[AgrPortfolioQueryResponseConnection] = field(
        default_factory=list,
        metadata={
            "name": "Connection",
            "type": "Element",
        }
    )

    def __post_init__(self):
        validate_list('dso_portfolios', self.dso_portfolios, AgrPortfolioQueryResponseDSOPortfolio, 1)




@dataclass(kw_only=True)
class AgrPortfolioQueryResponse(PayloadMessageResponse):
    """
    :ivar dso_view:
    :ivar time_zone: Time zone ID (as per the IANA time zone database,
        http://www.iana.org/time-zones, for example: Europe/Amsterdam)
        indicating the UTC offset that applies to the Period referenced
        in this message. Although the time zone is a market-wide fixed
        value, making this assumption explicit in each message is
        important for validation purposes, allowing implementations to
        reject messages with an errant UTC offset.
    :ivar period: The Period that the portfolio is valid.
    """
    class Meta:
        name = "AGRPortfolioQueryResponse"

    agr_portfolio_query_message_id: str = field(
        metadata={
            "name": "AGRPortfolioQueryMessageID",
            "type": "Attribute",
            "required": True,
            "pattern": r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}",
        }
    )

    dso_views: List[AgrPortfolioQueryResponseDSOView] = field(
        default_factory=list,
        metadata={
            "name": "DSO-View",
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
    period: XmlDate = field(
        metadata={
            "name": "Period",
            "type": "Attribute",
            "required": True,
        }
    )

    def __post_init__(self):
        self.dso_views = validate_list('dso_views', self.dso_views, AgrPortfolioQueryResponseDSOView, 1)


@dataclass(kw_only=True)
class AgrPortfolioQuery(PayloadMessage):
    """
    :ivar time_zone: Time zone ID (as per the IANA time zone database,
        http://www.iana.org/time-zones, for example: Europe/Amsterdam)
        indicating the UTC offset that applies to the Period referenced
        in this message. Although the time zone is a market-wide fixed
        value, making this assumption explicit in each message is
        important for validation purposes, allowing implementations to
        reject messages with an errant UTC offset.
    :ivar period: The Period for which the AGR requests the portfolio
        information.
    """

    class Meta:
        name = "AGRPortfolioQuery"

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
