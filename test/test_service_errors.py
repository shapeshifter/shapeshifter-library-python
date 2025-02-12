from base64 import b64decode, b64encode

import pytest
import requests
from nacl.bindings import crypto_sign

from shapeshifter_uftp.exceptions import ClientTransportException
from shapeshifter_uftp.transport import from_xml, seal_message, to_xml, unseal_message
from shapeshifter_uftp.uftp import (
    AcceptedRejected,
    AgrPortfolioUpdate,
    FlexOffer,
    FlexRequestResponse,
    PayloadMessageResponse,
    SignedMessage,
)

from .helpers.messages import messages_by_type
from .helpers.services import DummyAgrService, DummyCroService


def test_sender_mismatch():
    """
    Send a message with mismatching sender_domain in the outer
    envelope and the inner PayloadMessage.
    """
    with (
        DummyCroService() as cro_service,
        DummyAgrService() as agr_service
    ):
        with agr_service.cro_client(cro_service.sender_domain) as client:
            message = messages_by_type[AgrPortfolioUpdate]
            message.sender_domain = "fake.domain"

            sealed_message = seal_message(message, agr_service.signing_key)

            signed_message = SignedMessage(
                sender_domain=agr_service.sender_domain,
                sender_role="AGR",
                body=sealed_message
            )

            response = requests.post(
                client.recipient_endpoint,
                headers={"Content-Type": "text/xml"},
                data=to_xml(signed_message)
            )
            assert response.status_code == 200
            unsealed_response_message = agr_service.request_futures["process_agr_portfolio_update_response"].result(timeout=10)
            assert unsealed_response_message.result == AcceptedRejected.REJECTED
            assert unsealed_response_message.rejection_reason == 'Invalid Sender'



def test_transport_error():
    """
    Send a message with mismatching sender_domain in the outer
    envelope and the inner PayloadMessage.
    """
    with DummyCroService() as cro_service:
        agr_service = DummyAgrService()
        with agr_service.cro_client(cro_service.sender_domain) as client:
            message = b'<Hello />'
            sealed_message = crypto_sign(message, b64decode(agr_service.signing_key))
            signed_message = SignedMessage(
                sender_domain=agr_service.sender_domain,
                sender_role=agr_service.sender_role,
                body=sealed_message
            )
            response = requests.post(
                client.recipient_endpoint,
                headers={"Content-Type": "text/xml"},
                data=to_xml(signed_message)
            )

            assert response.status_code == 400
