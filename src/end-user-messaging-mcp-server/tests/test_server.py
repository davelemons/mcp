# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
# with the License. A copy of the License is located at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions
# and limitations under the License.
"""Tests for the end-user-messaging MCP Server."""

import pytest
from awslabs.end_user_messaging_mcp_server.server import send_text_message
from unittest.mock import MagicMock, patch
import os


@pytest.mark.asyncio
class TestSendTextMessage:
    """Tests for the SendTextMessage tool."""

    @pytest.fixture
    def mock_pinpoint_client(self, monkeypatch):
        """Create a mock pinpoint client."""
        mock_client = MagicMock()
        monkeypatch.setattr('awslabs.end_user_messaging_mcp_server.server.pinpoint_client', mock_client)
        return mock_client

    @pytest.fixture
    def mock_env_vars(self, monkeypatch):
        """Set up mock environment variables."""
        monkeypatch.setenv('SMS_ORIGINATION_IDENTITY', '+1987654321')
        monkeypatch.setenv('CONFIGURATION_SET_NAME', 'test-config-set')

    async def test_send_text_message_success_with_config_set(self, mock_pinpoint_client, mock_env_vars):
        """Test successful text message sending with configuration set from environment."""
        # Arrange
        destination_phone = '+1234567890'
        message = 'Test message'
        expected_message_id = 'test-message-id-123'
        
        mock_pinpoint_client.send_text_message.return_value = {'MessageId': expected_message_id}

        # Act
        result = await send_text_message(
            destination_phone_number=destination_phone,
            message=message
        )

        # Assert
        assert result == expected_message_id
        mock_pinpoint_client.send_text_message.assert_called_once_with(
            DestinationPhoneNumber=destination_phone,
            OriginationIdentity='+1987654321',
            MessageBody=message,
            ConfigurationSetName='test-config-set'
        )

    async def test_send_text_message_success_without_config_set(self, mock_pinpoint_client, monkeypatch):
        """Test successful text message sending without configuration set in environment."""
        # Arrange
        destination_phone = '+1234567890'
        message = 'Test message'
        expected_message_id = 'test-message-id-123'
        
        # Set only the required environment variable
        monkeypatch.setenv('SMS_ORIGINATION_IDENTITY', '+1987654321')
        monkeypatch.delenv('CONFIGURATION_SET_NAME', raising=False)
        
        mock_pinpoint_client.send_text_message.return_value = {'MessageId': expected_message_id}

        # Act
        result = await send_text_message(
            destination_phone_number=destination_phone,
            message=message
        )

        # Assert
        assert result == expected_message_id
        mock_pinpoint_client.send_text_message.assert_called_once_with(
            DestinationPhoneNumber=destination_phone,
            OriginationIdentity='+1987654321',
            MessageBody=message
        )

    async def test_send_text_message_missing_originator_identity(self, mock_pinpoint_client, monkeypatch):
        """Test handling of missing SMS_ORIGINATION_IDENTITY environment variable."""
        # Arrange
        destination_phone = '+1234567890'
        message = 'Test message'
        
        # Remove the required environment variable
        monkeypatch.delenv('SMS_ORIGINATION_IDENTITY', raising=False)

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await send_text_message(
                destination_phone_number=destination_phone,
                message=message
            )
        assert 'SMS_ORIGINATION_IDENTITY is not set' in str(exc_info.value)

    async def test_send_text_message_client_error(self, mock_pinpoint_client, mock_env_vars):
        """Test handling of client errors during text message sending."""
        # Arrange
        destination_phone = '+1234567890'
        message = 'Test message'
        
        mock_pinpoint_client.send_text_message.side_effect = Exception('AWS Client Error')

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await send_text_message(
                destination_phone_number=destination_phone,
                message=message
            )
        assert str(exc_info.value) == 'AWS Client Error'

    async def test_send_text_message_empty_config_set(self, mock_pinpoint_client, monkeypatch):
        """Test text message sending with empty configuration set in environment."""
        # Arrange
        destination_phone = '+1234567890'
        message = 'Test message'
        expected_message_id = 'test-message-id-123'
        
        # Set empty configuration set
        monkeypatch.setenv('SMS_ORIGINATION_IDENTITY', '+1987654321')
        monkeypatch.setenv('CONFIGURATION_SET_NAME', '')
        
        mock_pinpoint_client.send_text_message.return_value = {'MessageId': expected_message_id}

        # Act
        result = await send_text_message(
            destination_phone_number=destination_phone,
            message=message
        )

        # Assert
        assert result == expected_message_id
        mock_pinpoint_client.send_text_message.assert_called_once_with(
            DestinationPhoneNumber=destination_phone,
            OriginationIdentity='+1987654321',
            MessageBody=message
        )
