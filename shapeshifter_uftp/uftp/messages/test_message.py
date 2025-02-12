from dataclasses import dataclass, field
from typing import List, Optional

from xsdata.models.datatype import XmlDate, XmlDuration

from ..defaults import DEFAULT_TIME_ZONE
from ..enums import UsefRole
from ..validations import validate_list
from .flex_message import FlexMessage
from .payload_message import PayloadMessage, PayloadMessageResponse


@dataclass(kw_only=True)
class TestMessage(PayloadMessage):
    __test__ = False  # Tell pytest to ignore this class


@dataclass(kw_only=True)
class TestMessageResponse(PayloadMessageResponse):
    __test__ = False  # Tell pytest to ignore this class
