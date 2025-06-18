from datetime import datetime, timezone, timedelta

import requests

from .logging import logger

from typing import Optional
from threading import Lock

class AuthTokenManager:
    """
    A token manager that can be used to manage tokens for the Shapeshifter client.
    It handles OAuth2 Client Credentials flow to obtain and refresh tokens.
    This class is thread-safe and ensures that tokens are refreshed only when necessary.
    It provides a method to get request headers with the Bearer token included.
    """
    request_timeout: int = 30

    def __init__(self, 
                 oauth_token_endpoint: str,
                 oauth_client_id: str,
                 oauth_client_secret: str,
                 token_refresh_buffer: int = 30):
        self.oauth_token_endpoint = oauth_token_endpoint
        self.oauth_client_id = oauth_client_id
        self.oauth_client_secret = oauth_client_secret
        self.token_refresh_buffer = token_refresh_buffer
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._token_lock = Lock()

    def _is_oauth_configured(self) -> bool:
        """Check if OAuth2 is properly configured."""
        return all([
            self.oauth_token_endpoint,
            self.oauth_client_id,
            self.oauth_client_secret
        ])

    def _is_token_valid(self) -> bool:
        """Check if the current token is valid and not close to expiring."""
        if not self._access_token or not self._token_expires_at:
            return False
        
        buffer_time = datetime.now(timezone.utc) + timedelta(seconds=self.token_refresh_buffer)
        return self._token_expires_at > buffer_time

    def _obtain_bearer_token(self) -> str:
        """
        Obtain a Bearer token using OAuth2 Client Credentials flow.
        
        :return: Access token string
        :raises: Exception if token acquisition fails
        """
        if not self._is_oauth_configured():
            raise ValueError("OAuth2 not configured. Please provide oauth_token_endpoint, oauth_client_id, and oauth_client_secret.")

        token_data = {
            'grant_type': 'client_credentials',
            'client_id': self.oauth_client_id,
            'client_secret': self.oauth_client_secret
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
 
        try:
            response = requests.post(
                self.oauth_token_endpoint,
                data=token_data,
                headers=headers,
                timeout=self.request_timeout
            )
            response.raise_for_status()
            
            token_response = response.json()
            access_token = token_response['access_token']
            expires_in = token_response.get('expires_in', 300)
            
            self._token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
            
            logger.info(f"Successfully obtained OAuth2 token, expires at {self._token_expires_at}")
            return access_token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to obtain OAuth2 token: {e}")
            raise
        except KeyError as e:
            logger.error(f"Invalid token response format, missing key: {e}")
            raise

    def _get_valid_token(self) -> Optional[str]:
        """
        Get a valid Bearer token, refreshing if necessary.
        Thread-safe implementation.
        
        :return: Valid access token or None if OAuth2 not configured
        """
        if not self._is_oauth_configured():
            return None

        with self._token_lock:
            if not self._is_token_valid():
                logger.debug("Token invalid or expired, obtaining new token")
                self._access_token = self._obtain_bearer_token()
            
            return self._access_token

    def get_request_headers(self) -> dict:
        """
        Get headers for HTTP requests, including Bearer token if configured.
        
        :return: Dictionary of headers
        """
        headers = {"Content-Type": "text/xml; charset=utf-8"}
        
        token = self._get_valid_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        return headers