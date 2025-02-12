from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from xsdata.models.datatype import XmlDate, XmlDuration

from ..defaults import DEFAULT_TIME_ZONE
from ..enums import RedispatchBy
from ..validations import validate_list
from .flex_message import FlexMessage
from .payload_message import PayloadMessage, PayloadMessageResponse

# pylint: disable=missing-class-docstring,duplicate-code


@dataclass(kw_only=True)
class MeteringISP:
    """
    :ivar start: Number of the ISP this element refers to. The first ISP
        of a day has number 1.
    :ivar value: Metering, energy or price value at the end of this ISP,
        in the designated profile units.
    """
    class Meta:
        name = "MeteringISP"

    start: int = field(
        metadata={
            "name": "Start",
            "type": "Attribute",
            "required": True,
        }
    )
    value: Decimal = field(
        metadata={
            "name": "Value",
            "type": "Attribute",
            "required": True,
        }
    )


class MeteringProfileEnum(Enum):
    """
    :cvar POWER: The average active power during ISP, considering both
        import and export energy. Power=(ImportEnergy-
        ExportEnergy)*(60/ISP-Length-Minutes). For example with a 15
        minute ISP length we have a multiplier of 4, with a 30 minute
        ISP length we have a multiplier of 2. Including the power
        profile is recommended. It is expected that in the following
        major version the power will become a mandatory value.
    :cvar IMPORT_ENERGY: Imported active energy, consumed during the ISP
    :cvar EXPORT_ENERGY: Exported active energy, generated during the
        ISP
    :cvar IMPORT_METER_READING: Cumulative metered imported active
        energy reading, at the end of the ISP
    :cvar EXPORT_METER_READING: Cumulative metered exported active
        energy reading, at the end of the ISP
    """
    POWER = "Power"
    IMPORT_ENERGY = "ImportEnergy"
    EXPORT_ENERGY = "ExportEnergy"
    IMPORT_METER_READING = "ImportMeterReading"
    EXPORT_METER_READING = "ExportMeterReading"


class MeteringUnit(Enum):
    """
    :cvar K_W: kW must be used with Power profile values.
    :cvar K_WH: kWh must be used with energy profile values
        (ImportEnergy,ExportEnergy,ImportMeterReading,ExportMeterReading).
    """
    K_W = "kW"
    K_WH = "kWh"


@dataclass(kw_only=True)
class MeteringProfile:
    """
    A profile carries a sequence of ISPs with a defined type of metering data.
    """
    isps: List[MeteringISP] = field(
        default_factory=list,
        metadata={
            "name": "ISP",
            "type": "Element",
            "min_occurs": 1,
        }
    )
    profile_type: MeteringProfileEnum = field(
        metadata={
            "name": "ProfileType",
            "type": "Attribute",
            "required": True,
        }
    )
    unit: MeteringUnit = field(
        metadata={
            "name": "Unit",
            "type": "Attribute",
            "required": True,
        }
    )

    def __post_init__(self):
        validate_list('isps', self.isps, MeteringISP, 1)


@dataclass(kw_only=True)
class MeteringResponse(PayloadMessageResponse):
    metering_message_id: str = field(
        metadata={
            "name": "MeteringMessageID",
            "type": "Attribute",
            "required": True,
            "pattern": r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}",
        }
    )


@dataclass(kw_only=True)
class Metering(PayloadMessage):
    """
    :ivar profile:
    :ivar revision: Revision of this message. A sequence number that
        must be incremented each time a new revision of a metering
        message is sent.
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
    :ivar currency: ISO 4217 code indicating the currency that applies
        to the price of the Tariff Rates. Only required if ImportTariff
        or ExportTariff profiles are included.
    :ivar period: Day (in yyyy-mm-dd format) the ISPs referenced in this
        Metering message belong to.
    :ivar ean: EAN of the meter the message applies to.
    """
    profiles: List[MeteringProfile] = field(
        default_factory=list,
        metadata={
            "name": "Profile",
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
    isp_duration: XmlDuration = field(
        metadata={
            "name": "ISP-Duration",
            "type": "Attribute",
            "required": True,
        }
    )
    time_zone: str = field(
        metadata={
            "name": "TimeZone",
            "type": "Attribute",
            "required": True,
            "pattern": r"(Africa|America|Australia|Europe|Pacific)/[a-zA-Z0-9_/]{3,}",
        }
    )
    currency: Optional[str] = field(
        default=None,
        metadata={
            "name": "Currency",
            "type": "Attribute",
            "pattern": r"[A-Z]{3}",
        }
    )
    period: XmlDate = field(
        metadata={
            "name": "Period",
            "type": "Attribute",
            "required": True,
        }
    )
    ean: str = field(
        metadata={
            "name": "EAN",
            "type": "Attribute",
            "required": True,
            "pattern": r"[Ee][0-9]{16}",
        }
    )

    def __post_init__(self):
        validate_list('profiles', self.profiles, MeteringProfile, 1)
