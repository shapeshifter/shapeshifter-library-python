import pytest
from shapeshifter_uftp.uftp import destination_map
from shapeshifter_uftp import uftp
from shapeshifter_uftp import (
    ShapeshifterAgrService,
    ShapeshifterCroService,
    ShapeshifterDsoService,
    PayloadMessage,
    PayloadMessageResponse,
    TestMessage,
    TestMessageResponse,
    FlexMessage,
)


@pytest.mark.parametrize(
    "message_cls",
    [
        getattr(uftp, message_cls)
        for message_cls in dir(uftp)
        if isinstance(getattr(uftp, message_cls), type)
        and PayloadMessage in getattr(uftp, message_cls).__mro__
        and getattr(uftp, message_cls) not in (
            PayloadMessage,
            PayloadMessageResponse,
            TestMessage,
            TestMessageResponse,
            FlexMessage,
        )
    ],
)
def test_all_messages_have_destination(message_cls):
    assert message_cls in destination_map


@pytest.mark.parametrize("message_cls,destination", destination_map.items())
def test_message_destination(message_cls, destination):
    service_map = {
        "AGR": ShapeshifterAgrService,
        "CRO": ShapeshifterCroService,
        "DSO": ShapeshifterDsoService,
    }
    assert message_cls in service_map[destination].acceptable_messages
