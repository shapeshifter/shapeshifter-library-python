from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional

from xsdata.models.datatype import XmlDate, XmlDuration

from .common import (
    AcceptedDisputed,
    AvailableRequested,
    PayloadMessage,
    PayloadMessageResponse,
)
from .defaults import DEFAULT_TIME_ZONE
from .validations import validate_decimal, validate_list

# pylint: disable=missing-class-docstring,duplicate-code,too-many-lines
















