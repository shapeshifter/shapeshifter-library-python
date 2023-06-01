import pytest
from shapeshifter_uftp.uftp import routing_map
from shapeshifter_uftp.client import client_map
from .helpers.messages import messages
from shapeshifter_uftp.service.base_service import snake_case


@pytest.mark.parametrize(
    'message',
    messages,
    ids=[message.__class__.__name__ for message in messages]
)
def test_presence_of_client_methods(message):
    client = client_map[routing_map[message.__class__]]
    expected_method = f"send_{snake_case(message.__class__.__name__)}"
    assert hasattr(client, expected_method)
