from .helpers.services import DummyAgrService, DummyCroService
from .helpers.messages import messages_by_type
from shapeshifter_uftp.uftp import FlexRequestResponse, AcceptedRejected, SignedMessage, AgrPortfolioUpdate, PayloadMessageResponse
from shapeshifter_uftp.transport import seal_message, unseal_message, to_xml, from_xml
import requests
from nacl.bindings import crypto_sign
from base64 import b64encode, b64decode


def test_unacceptable_message():
    with DummyCroService() as cro_service:
        agr_service = DummyAgrService()
        with agr_service.cro_client(cro_service.sender_domain) as client:
            response = client._send_message(messages_by_type[FlexRequestResponse])
            assert response.result == AcceptedRejected.REJECTED
            assert response.rejection_reason == "Invalid Message: 'FlexRequestResponse'"


def test_sender_mismatch():
    """
    Send a message with mismatching sender_domain in the outer
    envelope and the inner PayloadMessage.
    """
    with DummyCroService() as cro_service:
        agr_service = DummyAgrService()
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
            sealed_response_message = from_xml(response.content)
            unsealed_response_message = unseal_message(sealed_response_message.body, client.recipient_signing_key)
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
                body=b64encode(sealed_message)
            )
            response = requests.post(
                client.recipient_endpoint,
                headers={"Content-Type": "text/xml"},
                data=to_xml(signed_message)
            )

            assert response.status_code == 400


def test_error_during_post_process():
    def faulty_post_process(self, message):
        raise ValueError("BOOM")

    with DummyCroService() as cro_service:
        agr_service = DummyAgrService()
        cro_service.process_agr_portfolio_update = faulty_post_process
        cro_service.response_futures["pre_process_agr_portfolio_update"].set_result(PayloadMessageResponse())
        with agr_service.cro_client(cro_service.sender_domain) as client:
            result = client.send_agr_portfolio_update(messages_by_type[AgrPortfolioUpdate])
            assert result.result == AcceptedRejected.ACCEPTED
