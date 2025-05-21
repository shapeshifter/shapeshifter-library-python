from contextlib import contextmanager
from datetime import datetime
from json import JSONDecodeError

import requests


class OAuthClient:

    EXPIRATION_SAFETY_BUFFER = 60

    def __init__(self, url, client_id, client_secret):
        self.url = url
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.access_token_type = None
        self.access_token_expiry = None

    @contextmanager
    def ensure_authenticated(self):
        if not self.authenticated:
            self.authenticate()
        yield

    @property
    def authenticated(self):
        return self.access_token and not self.expired

    @property
    def expired(self):
        return self.access_token_expiry < (datetime.now().timestamp() + OAuthClient.EXPIRATION_SAFETY_BUFFER)

    @property
    def auth_header(self):
        return {"Authorization": f"{self.access_token_type} {self.access_token}"}

    def authenticate(self):
        response = requests.post(
            self.url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            timeout=30
        )

        if response.status_code != 200:
            raise AuthorizationError(
                f"Could not obtain an access token from the OAuth server at {self.url}:"
                f"{response.text}"
            )
        try:
            response_data = response.json()
        except JSONDecodeError as err:
            raise AuthorizationError(
                f"The OAuth server at {self.url} did not return a valid JSON response: "
                f"{response.text}"
            ) from err

        try:
            self.access_token = response_data["access_token"]
            self.access_token_type = response_data["token_type"]
            self.access_token_expiry = datetime.now().timestamp() + response_data["expires_in"]
        except KeyError as err:
            raise AuthorizationError(
                f"The response from the OAuth server is missing the {str(err)} field"
            ) from err


class PassthroughOAuthClient:

    auth_header = {}

    @contextmanager
    def ensure_authenticated(self):
        yield


class AuthorizationError(Exception):
    pass
