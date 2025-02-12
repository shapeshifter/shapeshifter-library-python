from unittest.mock import patch

import pytest
from nacl.bindings import crypto_sign_keypair

from shapeshifter_uftp.exceptions import ClientTransportException, SchemaException
from shapeshifter_uftp.uftp import FlexRequestResponse

from .helpers.messages import messages_by_type
from .helpers.services import DummyAgrService, DummyDsoService

fake_keypair = crypto_sign_keypair()


def test_send_non_payload_message():
    service = DummyAgrService()
    dso_service = DummyDsoService()
    client = service.dso_client(dso_service.sender_domain)
    with pytest.raises(TypeError):
        client._send_message("Hello there")
