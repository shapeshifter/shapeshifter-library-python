from dataclasses import dataclass, field
from typing import List, Optional

from xsdata.models.datatype import XmlDate

from .common import PayloadMessage, PayloadMessageResponse, RedispatchBy
from .defaults import DEFAULT_TIME_ZONE
from .validations import validate_list

# pylint: disable=missing-class-docstring,duplicate-code

