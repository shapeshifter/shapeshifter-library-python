import pytest
from time import sleep
from concurrent.futures import ThreadPoolExecutor

from shapeshifter_uftp.uftp import routing_map, PayloadMessageResponse, AcceptedRejected
from shapeshifter_uftp.service.base_service import snake_case
from .helpers.messages import messages
from .helpers.services import DummyAgrService, DummyCroService, DummyDsoService


# These fixtures allow us to only start up the services once and use
# them for all the parametrized test cases, which speeds up testing.
@pytest.fixture(scope='module')
def agr_service():
    with DummyAgrService() as service:
        yield service

@pytest.fixture(scope='module')
def cro_service():
    with DummyCroService() as service:
        yield service

@pytest.fixture(scope='module')
def dso_service():
    with DummyDsoService() as service:
        yield service


@pytest.mark.parametrize(
    'message',
    messages,
    ids=[message.__class__.__name__ for message in messages]
)
def test_communications(message, agr_service, cro_service, dso_service):
    service_map = {
        "AGR": agr_service,
        "CRO": cro_service,
        "DSO": dso_service,
    }

    sender_role, recipient_role = routing_map[type(message)]
    sender = service_map[sender_role]
    recipient = service_map[recipient_role]
    client_method = f"{recipient.sender_role.lower()}_client"
    with ThreadPoolExecutor() as executor:
        with getattr(sender, client_method)(recipient.sender_domain) as client:
            sending_method = f"send_{snake_case(message.__class__.__name__)}"
            main_future = executor.submit(getattr(client, sending_method), message)

        assert recipient.request_futures[f"pre_process_{snake_case(message.__class__.__name__)}"].result() == message
        response_message = PayloadMessageResponse()
        recipient.response_futures[f"pre_process_{snake_case(message.__class__.__name__)}"].set_result(response_message)
        assert recipient.request_futures[f"process_{snake_case(message.__class__.__name__)}"].result() == message
        assert main_future.result().result == AcceptedRejected.ACCEPTED
