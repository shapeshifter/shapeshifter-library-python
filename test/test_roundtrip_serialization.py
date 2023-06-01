import pytest
from shapeshifter_uftp.transport import from_json, to_json, from_xml, to_xml
from .helpers.messages import messages


@pytest.mark.parametrize(
    "message", messages, ids=[message.__class__.__name__ for message in messages]
)
def test_roundtrip_json(message):
    serialized = to_json(message)
    parsed = from_json(serialized, type(message))
    assert parsed == message


@pytest.mark.parametrize(
    "message", messages, ids=[message.__class__.__name__ for message in messages]
)
def test_roundtrip_xml(message):
    serialized = to_xml(message)
    parsed = from_xml(serialized)
    assert parsed == message
