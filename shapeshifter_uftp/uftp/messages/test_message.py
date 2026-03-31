from dataclasses import dataclass

from .payload_message import PayloadMessage, PayloadMessageResponse


@dataclass(kw_only=True)
class TestMessage(PayloadMessage):
    __test__ = False  # Tell pytest to ignore this class


@dataclass(kw_only=True)
class TestMessageResponse(PayloadMessageResponse):
    __test__ = False  # Tell pytest to ignore this class
