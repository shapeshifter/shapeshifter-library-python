import pytest
from shapeshifter_uftp.exceptions import ClientTransportException, SchemaException
from .helpers.services import DummyAgrService, DummyDsoService
from .helpers.messages import messages_by_type
from shapeshifter_uftp.uftp import FlexRequestResponse
from unittest.mock import patch

from nacl.bindings import crypto_sign_keypair

fake_keypair = crypto_sign_keypair()


def test_send_non_payload_message():
    service = DummyAgrService()
    dso_service = DummyDsoService()
    client = service.dso_client(dso_service.sender_domain)
    with pytest.raises(TypeError):
        client._send_message("Hello there")


def test_non_200_status_code():
    def fake_pre_process_flex_request_response(self, message):
        raise SchemaException()
    with DummyDsoService() as dso_service:
        with patch.object(dso_service, 'pre_process_flex_request_response', new=fake_pre_process_flex_request_response):
            dso_service.pre_process_flex_request_response = fake_pre_process_flex_request_response
            agr_service = DummyAgrService()
            with agr_service.dso_client(dso_service.sender_domain) as client:
                with pytest.raises(ClientTransportException) as err:
                    client.send_flex_request_response(messages_by_type[FlexRequestResponse])
                    assert err.response.status_code == SchemaException.http_status_code

