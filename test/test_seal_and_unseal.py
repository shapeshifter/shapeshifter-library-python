from base64 import b64encode, b64decode
from datetime import datetime, timezone
from nacl.bindings import crypto_sign_keypair, crypto_sign, crypto_sign_open
import pytest
import re
from socket import socket

from shapeshifter_uftp import TestMessage as UFTPTestMessage
from shapeshifter_uftp.transport import seal_message, unseal_message, get_key
from shapeshifter_uftp.exceptions import SchemaException, InvalidSignatureException

public, private = crypto_sign_keypair()
public_base64 = b64encode(public)
private_base64 = b64encode(private)


def test_seal_unseal_message():
    msg = UFTPTestMessage(
        version="3.0.0",
        sender_domain="dso.dev",
        recipient_domain="cro.dev",
        time_stamp=datetime.now(timezone.utc).isoformat(),
        message_id="1234",
        conversation_id="1234"
    )
    msg.version = "3.0.0"
    sealed = seal_message(msg, private_base64)
    unsealed = unseal_message(sealed, public_base64)
    assert msg == unsealed


def test_tampered_message():
    msg = UFTPTestMessage(
        version="3.0.0",
        sender_domain="dso.dev",
        recipient_domain="cro.dev",
        time_stamp=datetime.now(timezone.utc).isoformat(),
        message_id="1234",
        conversation_id="1234"
    )
    msg.version = "3.0.0"
    sealed = seal_message(msg, private_base64)
    sealed = bytes([sealed[0] + 1]) + sealed[1:]
    with pytest.raises((InvalidSignatureException, SchemaException)):
        unseal_message(sealed, public_base64)


def test_invalid_message():
    msg = '<?xml version="1.0" encoding="UTF-8"?><Hello />'.encode()
    sealed = crypto_sign(msg, private)
    with pytest.raises(SchemaException):
        unsealed = unseal_message(sealed, public_base64)


def test_seal_invalid_type():
    msg = "Hello"
    with pytest.raises(TypeError):
        sealed = seal_message(msg, private_base64)

def test_get_key():
    key = get_key("enexis.dev", "dso")
    assert re.match(r'[0-9A-Za-z+/=]{44}', key)
