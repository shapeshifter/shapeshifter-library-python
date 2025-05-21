from datetime import datetime

import pytest
import responses

from shapeshifter_uftp import FlexOffer, OAuthClient, ShapeshifterAgrDsoClient
from shapeshifter_uftp.oauth import AuthorizationError

from .helpers.messages import messages_by_type
from .helpers.services import (
    AGR_PRIVATE_KEY,
    AGR_PUBLIC_KEY,
    DSO_PUBLIC_KEY,
    DummyAgrService,
)

OAUTH_URL = "https://oauth.dummy.server"
CLIENT_ID = "client-id"
CLIENT_SECRET = "client-secret"
ACCESS_TOKEN = "access-token"

@pytest.fixture
def oauth_client(*args, **kwargs):
    return OAuthClient(
        url=OAUTH_URL,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )

@responses.activate
def test_oauth_client(oauth_client):
    now = datetime.now().timestamp()
    responses.add(
        method=responses.POST,
        url=OAUTH_URL,
        status=200,
        json={
            "access_token": ACCESS_TOKEN,
            "token_type": "Bearer",
            "expires_in": 300
        }
    )

    oauth_client.authenticate()

    assert oauth_client.access_token == ACCESS_TOKEN
    assert oauth_client.access_token_type == "Bearer"
    assert now + 300 < oauth_client.access_token_expiry < now + 301


@responses.activate
def test_oauth_shapeshifter_client(oauth_client):
    responses.add(
        method=responses.POST,
        url=OAUTH_URL,
        status=200,
        json={
            "access_token": ACCESS_TOKEN,
            "token_type": "Bearer",
            "expires_in": 300
        }
    )

    responses.add(
        responses.POST,
        "http://localhost:9003/shapeshifter/api/v3/message"
    )

    client = ShapeshifterAgrDsoClient(
        sender_domain="agr.dev",
        signing_key=AGR_PRIVATE_KEY,
        recipient_domain="dso.dev",
        recipient_endpoint="http://localhost:9003/shapeshifter/api/v3/message",
        recipient_signing_key=DSO_PUBLIC_KEY,
        oauth_client=oauth_client
    )

    response = client.send_flex_offer(messages_by_type[FlexOffer])
    assert response is None


@responses.activate
def test_oauth_shapeshifter_client_failed(oauth_client):
    responses.add(
        method=responses.POST,
        url=OAUTH_URL,
        status=400,
        json={
            "error": "invalid_request",
            "error_description": "Could not process"
        }
    )

    responses.add(
        responses.POST,
        "http://localhost:9003/shapeshifter/api/v3/message"
    )

    client = ShapeshifterAgrDsoClient(
        sender_domain="agr.dev",
        signing_key=AGR_PRIVATE_KEY,
        recipient_domain="dso.dev",
        recipient_endpoint="http://localhost:9003/shapeshifter/api/v3/message",
        recipient_signing_key=DSO_PUBLIC_KEY,
        oauth_client=oauth_client
    )

    with pytest.raises(AuthorizationError):
        response = client.send_flex_offer(messages_by_type[FlexOffer])

@responses.activate
def test_oauth_shapeshifter_service():
    def oauth_lookup_function(sender_domain, sender_role):
        return OAuthClient(
            url=OAUTH_URL,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
        )

    service = DummyAgrService(
        oauth_lookup_function=oauth_lookup_function
    )

    client = service.dso_client("dso.dev")
    assert isinstance(client.oauth_client, OAuthClient)
    assert client.oauth_client.url == OAUTH_URL
    assert client.oauth_client.client_id == CLIENT_ID
    assert client.oauth_client.client_secret == CLIENT_SECRET

