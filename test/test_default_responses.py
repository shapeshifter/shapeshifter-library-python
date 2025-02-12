import pytest

from shapeshifter_uftp.service.base_service import snake_case
from shapeshifter_uftp.uftp import AcceptedRejected, PayloadMessageResponse, routing_map

from .helpers.messages import messages
from .helpers.services import (
    DefaultResponseAgrService,
    DefaultResponseCroService,
    DefaultResponseDsoService,
)


# These fixtures allow us to only start up the services once and use
# them for all the parametrized test cases, which speeds up testing.
@pytest.fixture(scope='module')
def default_agr_service():
    with DefaultResponseAgrService() as service:
        yield service

@pytest.fixture(scope='module')
def default_cro_service():
    with DefaultResponseCroService() as service:
        yield service

@pytest.fixture(scope='module')
def default_dso_service():
    with DefaultResponseDsoService() as service:
        yield service



@pytest.mark.parametrize(
    'message',
    messages,
    ids=[message.__class__.__name__ for message in messages]
)
def test_default_responses(message, default_agr_service, default_cro_service, default_dso_service):
    service_map = {
        "AGR": default_agr_service,
        "CRO": default_cro_service,
        "DSO": default_dso_service,
    }

    sender_role, recipient_role = routing_map[type(message)]
    sender = service_map[sender_role]
    recipient = service_map[recipient_role]

    client_method = f"{recipient.sender_role.lower()}_client"
    sending_method = f"send_{snake_case(message.__class__.__name__)}"

    client = getattr(sender, client_method)(recipient.sender_domain)
    response = getattr(client, sending_method)(message)

    assert response is None
