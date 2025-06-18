import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta
import json
import time

from shapeshifter_uftp.token_manager import AuthTokenManager
from shapeshifter_uftp.service.base_service import ShapeshifterService
from shapeshifter_uftp.client.base_client import ShapeshifterClient
from shapeshifter_uftp.uftp import PayloadMessage


class TestAuthTokenManager:
    """Test suite for AuthTokenManager class"""
    
    @pytest.fixture
    def token_manager(self):
        """Fixture for AuthTokenManager instance"""
        return AuthTokenManager(
            oauth_token_endpoint="https://test.example.com/oauth2/token",
            oauth_client_id="test_client_id",
            oauth_client_secret="test_client_secret",
            token_refresh_buffer=30
        )
    
    def test_init(self, token_manager):
        """Test AuthTokenManager initialization"""
        assert token_manager.oauth_token_endpoint == "https://test.example.com/oauth2/token"
        assert token_manager.oauth_client_id == "test_client_id"
        assert token_manager.oauth_client_secret == "test_client_secret"
        assert token_manager.token_refresh_buffer == 30
        assert token_manager._access_token is None
        assert token_manager._token_expires_at is None
    
    def test_is_oauth_configured(self, token_manager):
        """Test OAuth2 configuration check"""
        assert token_manager._is_oauth_configured() is True
        
        # Test with missing configuration
        incomplete_manager = AuthTokenManager("", "", "")
        assert incomplete_manager._is_oauth_configured() is False
    
    def test_is_token_valid_no_token(self, token_manager):
        """Test token validity when no token exists"""
        assert token_manager._is_token_valid() is False
    
    def test_is_token_valid_expired(self, token_manager):
        """Test token validity when token is expired"""
        token_manager._access_token = "test_token"
        token_manager._token_expires_at = datetime.now(timezone.utc) - timedelta(seconds=60)
        assert token_manager._is_token_valid() is False
    
    def test_is_token_valid_near_expiry(self, token_manager):
        """Test token validity when token is near expiry (within buffer)"""
        token_manager._access_token = "test_token"
        token_manager._token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=20)
        assert token_manager._is_token_valid() is False
    
    def test_is_token_valid_good_token(self, token_manager):
        """Test token validity when token is valid"""
        token_manager._access_token = "test_token"
        token_manager._token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=300)  # 5 minutes
        assert token_manager._is_token_valid() is True
    
    @patch('requests.post')
    def test_obtain_bearer_token_success(self, mock_post, token_manager):
        """Test successful token acquisition"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'access_token': 'test_access_token_123',
            'expires_in': 300
        }
        mock_post.return_value = mock_response
        
        token = token_manager._obtain_bearer_token()
        
        assert token == 'test_access_token_123'
        assert token_manager._token_expires_at is not None
        
        mock_post.assert_called_once_with(
            "https://test.example.com/oauth2/token",
            data={
                'grant_type': 'client_credentials',
                'client_id': 'test_client_id',
                'client_secret': 'test_client_secret'
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
    
    @patch('requests.post')
    def test_obtain_bearer_token_http_error(self, mock_post, token_manager):
        """Test token acquisition with HTTP error"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Unauthorized")
        mock_post.return_value = mock_response
        
        with pytest.raises(requests.exceptions.HTTPError):
            token_manager._obtain_bearer_token()
    
    @patch('requests.post')
    def test_obtain_bearer_token_invalid_response(self, mock_post, token_manager):
        """Test token acquisition with invalid JSON response"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {'invalid': 'response'}  # Missing access_token
        mock_post.return_value = mock_response
        
        with pytest.raises(KeyError):
            token_manager._obtain_bearer_token()
    
    @patch.object(AuthTokenManager, '_obtain_bearer_token')
    def test_get_valid_token_refresh_needed(self, mock_obtain, token_manager):
        """Test getting valid token when refresh is needed"""
        mock_obtain.return_value = 'new_token_123'
        
        # Set up expired token
        token_manager._access_token = 'old_token'
        token_manager._token_expires_at = datetime.now(timezone.utc) - timedelta(seconds=60)
        
        token = token_manager._get_valid_token()
        
        assert token == 'new_token_123'
        mock_obtain.assert_called_once()
    
    def test_get_valid_token_no_refresh_needed(self, token_manager):
        """Test getting valid token when no refresh is needed"""
        # Set up valid token
        token_manager._access_token = 'valid_token'
        token_manager._token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=300)
        
        with patch.object(token_manager, '_obtain_bearer_token') as mock_obtain:
            token = token_manager._get_valid_token()
            
            assert token == 'valid_token'
            mock_obtain.assert_not_called()
    
    @patch.object(AuthTokenManager, '_get_valid_token')
    def test_get_request_headers_with_token(self, mock_get_token, token_manager):
        """Test getting request headers with Bearer token"""
        mock_get_token.return_value = 'test_bearer_token'
        
        headers = token_manager.get_request_headers()
        
        expected_headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "Authorization": "Bearer test_bearer_token"
        }
        assert headers == expected_headers
    
    @patch.object(AuthTokenManager, '_get_valid_token')
    def test_get_request_headers_no_token(self, mock_get_token, token_manager):
        """Test getting request headers without Bearer token"""
        mock_get_token.return_value = None
        
        headers = token_manager.get_request_headers()
        
        expected_headers = {"Content-Type": "text/xml; charset=utf-8"}
        assert headers == expected_headers
        assert "Authorization" not in headers


class TestShapeshifterServiceOAuth:
    """Test suite for ShapeshifterService OAuth2 integration"""
    
    def test_service_with_oauth_config(self):
        """Test service initialization with OAuth2 configuration"""
        service = ShapeshifterService(
            sender_domain="test.example.com",
            signing_key="test_signing_key",
            oauth_token_endpoint="https://oauth.example.com/token",
            oauth_client_id="test_client",
            oauth_client_secret="test_secret",
            token_refresh_buffer=60
        )
        
        assert service.auth_token_manager is not None
        assert service.auth_token_manager.oauth_token_endpoint == "https://oauth.example.com/token"
        assert service.auth_token_manager.oauth_client_id == "test_client"
        assert service.auth_token_manager.oauth_client_secret == "test_secret"
        assert service.auth_token_manager.token_refresh_buffer == 60
    
    def test_service_without_oauth_config(self):
        """Test service initialization without OAuth2 configuration"""
        service = ShapeshifterService(
            sender_domain="test.example.com",
            signing_key="test_signing_key",
            oauth_token_endpoint=None,
            oauth_client_id=None,
            oauth_client_secret=None
        )
        
        assert service.auth_token_manager is None
    
    @patch('shapeshifter_uftp.service.base_service.client_map')
    @patch('shapeshifter_uftp.service.base_service.transport')
    def test_get_client_with_oauth(self, mock_transport, mock_client_map):
        """Test _get_client method passes OAuth token manager"""
        # Setup mocks
        mock_client_class = Mock()
        mock_client_map.__getitem__.return_value = mock_client_class
        mock_transport.get_endpoint.return_value = "https://recipient.example.com/api"
        mock_transport.get_key.return_value = "recipient_public_key"
        
        # Create service with OAuth2
        service = ShapeshifterService(
            sender_domain="test.example.com",
            signing_key="test_signing_key",
            oauth_token_endpoint="https://oauth.example.com/token",
            oauth_client_id="test_client",
            oauth_client_secret="test_secret"
        )
        service.sender_role = "AGR"  # Set sender role for client_map lookup
        
        # Call _get_client
        client = service._get_client("recipient.example.com", "DSO")
        
        # Verify client was created with oauth_token_manager
        mock_client_class.assert_called_once()
        call_kwargs = mock_client_class.call_args[1]
        assert call_kwargs['oauth_token_manager'] == service.auth_token_manager


class TestShapeshifterClientOAuth:
    """Test suite for ShapeshifterClient OAuth2 integration"""
    
    @pytest.fixture
    def mock_token_manager(self):
        """Fixture for mock token manager"""
        return Mock(spec=AuthTokenManager)
    
    @pytest.fixture
    def client_with_oauth(self, mock_token_manager):
        """Fixture for client with OAuth2"""
        client = ShapeshifterClient(
            sender_domain="sender.example.com",
            recipient_domain="recipient.example.com",
            recipient_endpoint="https://recipient.example.com/api",
            signing_key="test_signing_key",
            recipient_signing_key="recipient_public_key",
            oauth_token_manager=mock_token_manager
        )
        client.sender_role = "test_sender"
        client.recipient_role = "test_recipient"
        return client
    
    @pytest.fixture
    def client_without_oauth(self):
        """Fixture for client without OAuth2"""
        client = ShapeshifterClient(
            sender_domain="sender.example.com",
            recipient_domain="recipient.example.com",
            recipient_endpoint="https://recipient.example.com/api",
            signing_key="test_signing_key",
            recipient_signing_key="recipient_public_key"
        )
        client.sender_role = "test_sender"
        client.recipient_role = "test_recipient"
        return client
    
    @pytest.fixture
    def mock_payload_message(self):
        """Fixture for mock PayloadMessage"""
        mock_message = Mock(spec=PayloadMessage)
        # Set required attributes that _send_message expects
        mock_message.__class__.__name__ = "TestMessage"
        mock_message.version = None
        mock_message.sender_domain = None
        mock_message.recipient_domain = None
        mock_message.time_stamp = None
        mock_message.message_id = None
        mock_message.conversation_id = None
        return mock_message
    
    @patch('requests.post')
    @patch('shapeshifter_uftp.client.base_client.transport')
    def test_send_message_with_oauth_success(self, mock_transport, mock_post, client_with_oauth, mock_token_manager, mock_payload_message):
        """Test _send_message with successful OAuth2 token"""
        # Setup mocks
        mock_token_manager.get_request_headers.return_value = {
            "Content-Type": "text/xml; charset=utf-8",
            "Authorization": "Bearer test_token_123"
        }
        
        mock_transport.seal_message.return_value = "sealed_message"
        mock_transport.to_xml.return_value = "<xml>message</xml>"
        mock_transport.parser.from_bytes.return_value = Mock(body="sealed_response")
        mock_transport.unseal_message.return_value = "unsealed_response"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"<xml>response</xml>"
        mock_post.return_value = mock_response
        
        # Create a mock message
        # mock_message = Mock(spec=PayloadMessage)
        # mock_message.__class__.__name__ = "TestMessage"
        
        # Call _send_message
        result = client_with_oauth._send_message(mock_payload_message)
        
        # Verify OAuth2 headers were used
        mock_token_manager.get_request_headers.assert_called_once()
        mock_post.assert_called_once()
        
        # Check that the Authorization header was included
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs['headers']['Authorization'] == "Bearer test_token_123"
    
    @patch('requests.post')
    @patch('shapeshifter_uftp.client.base_client.transport')
    def test_send_message_oauth_failure_fallback(self, mock_transport, mock_post, client_with_oauth, mock_token_manager, mock_payload_message):
        """Test _send_message falls back to basic headers when OAuth2 fails"""
        # Setup OAuth2 to fail
        mock_token_manager.get_request_headers.side_effect = Exception("OAuth2 failed")
        
        mock_transport.seal_message.return_value = "sealed_message"
        mock_transport.to_xml.return_value = "<xml>message</xml>"
        mock_transport.parser.from_bytes.return_value = Mock(body="sealed_response")
        mock_transport.unseal_message.return_value = "unsealed_response"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"<xml>response</xml>"
        mock_post.return_value = mock_response
        
        # # Create a mock message
        # mock_message = Mock()
        # mock_message.__class__.__name__ = "TestMessage"
        
        # Call _send_message
        result = client_with_oauth._send_message(mock_payload_message)
        
        # Verify fallback headers were used
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs['headers'] == {"Content-Type": "text/xml; charset=utf-8"}
        assert "Authorization" not in call_kwargs['headers']
    
    @patch('requests.post')
    @patch('shapeshifter_uftp.client.base_client.transport')
    def test_send_message_without_oauth(self, mock_transport, mock_post, client_without_oauth, mock_payload_message):
        """Test _send_message without OAuth2 token manager"""
        mock_transport.seal_message.return_value = "sealed_message"
        mock_transport.to_xml.return_value = "<xml>message</xml>"
        mock_transport.parser.from_bytes.return_value = Mock(body="sealed_response")
        mock_transport.unseal_message.return_value = "unsealed_response"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"<xml>response</xml>"
        mock_post.return_value = mock_response
        
        # Call _send_message
        result = client_without_oauth._send_message(mock_payload_message)
        
        # Verify basic headers were used
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs['headers'] == {"Content-Type": "text/xml; charset=utf-8"}
        assert "Authorization" not in call_kwargs['headers']


class TestTokenRefreshLogic:
    """Test token refresh timing and logic"""
    
    @pytest.fixture
    def token_manager(self):
        return AuthTokenManager(
            oauth_token_endpoint="https://test.example.com/oauth2/token",
            oauth_client_id="test_client_id",
            oauth_client_secret="test_client_secret",
            token_refresh_buffer=30
        )
    
    @pytest.mark.parametrize("expires_in_seconds,refresh_buffer,should_refresh", [
        (300, 30, False),  # 5 minutes left, 30s buffer - no refresh needed
        (25, 30, True),    # 25 seconds left, 30s buffer - refresh needed
        (30, 30, True),    # Exactly at buffer - refresh needed
        (31, 30, False),   # Just over buffer - no refresh needed
        (0, 30, True),     # Expired - refresh needed
    ])
    def test_token_refresh_timing(self, token_manager, expires_in_seconds, refresh_buffer, should_refresh):
        """Test token refresh timing with different scenarios"""
        token_manager.token_refresh_buffer = refresh_buffer
        token_manager._access_token = "test_token"
        token_manager._token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in_seconds)
        
        result = token_manager._is_token_valid()
        assert result != should_refresh  # should_refresh means token is NOT valid


class TestErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.fixture
    def token_manager(self):
        return AuthTokenManager(
            oauth_token_endpoint="https://test.example.com/oauth2/token",
            oauth_client_id="test_client_id",
            oauth_client_secret="test_client_secret",
            token_refresh_buffer=30
        )
    
    @patch('requests.post')
    def test_network_timeout(self, mock_post, token_manager):
        """Test handling of network timeouts"""
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")
        
        with pytest.raises(requests.exceptions.Timeout):
            token_manager._obtain_bearer_token()
    
    @patch('requests.post')
    def test_connection_error(self, mock_post, token_manager):
        """Test handling of connection errors"""
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        with pytest.raises(requests.exceptions.ConnectionError):
            token_manager._obtain_bearer_token()
    
    @patch('requests.post')
    def test_invalid_json_response(self, mock_post, token_manager):
        """Test handling of invalid JSON response"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_post.return_value = mock_response
        
        with pytest.raises(json.JSONDecodeError):
            token_manager._obtain_bearer_token()


# Pytest configuration
@pytest.fixture(scope="session")
def setup_logging():
    """Setup logging for tests"""
    import logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


# Parametrized tests for different scenarios
@pytest.mark.parametrize("endpoint,client_id,secret,expected_configured", [
    ("https://oauth.example.com/token", "client123", "secret456", True),
    ("", "client123", "secret456", False),
    ("https://oauth.example.com/token", "", "secret456", False),
    ("https://oauth.example.com/token", "client123", "", False),
    (None, None, None, False),
])
def test_oauth_configuration_scenarios(endpoint, client_id, secret, expected_configured):
    """Test different OAuth2 configuration scenarios"""
    if endpoint is None:
        # Handle case where service is created without OAuth2 params
        service = ShapeshifterService(
            sender_domain="test.example.com",
            signing_key="test_key",
            oauth_token_endpoint=None,
            oauth_client_id=None,
            oauth_client_secret=None
        )
        assert (service.auth_token_manager is not None) == expected_configured
    else:
        token_manager = AuthTokenManager(
            oauth_token_endpoint=endpoint,
            oauth_client_id=client_id,
            oauth_client_secret=secret
        )
        assert token_manager._is_oauth_configured() == expected_configured