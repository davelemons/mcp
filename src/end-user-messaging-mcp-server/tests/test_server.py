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
from unittest.mock import MagicMock, ANY


@pytest.mark.asyncio
class TestSendTextMessage:
    """Tests for the SendTextMessage tool."""

    @pytest.fixture
    def mock_pinpoint_client(self, monkeypatch):
        """Create a mock pinpoint client."""
        mock_client = MagicMock()
        monkeypatch.setattr('awslabs.end_user_messaging_mcp_server.server.pinpoint_client', mock_client)
        return mock_client

    async def test_send_text_message_success(self, mock_pinpoint_client):
        """Test successful text message sending without configuration set."""
        # Arrange
        destination_phone = '+1234567890'
        originator = '+1987654321'
        message = 'Test message'
        expected_message_id = 'test-message-id-123'
        
        mock_pinpoint_client.send_text_message.return_value = {'MessageId': expected_message_id}

        # Act
        result = await send_text_message(
            destination_phone_number=destination_phone,
            originator_identity=originator,
            message=message
        )

        # Assert
        assert result == expected_message_id
        mock_pinpoint_client.send_text_message.assert_called_once_with(
            DestinationPhoneNumber=destination_phone,
            OriginationIdentity=originator,
            MessageBody=message,
            ConfigurationSetName=ANY
        )

    async def test_send_text_message_with_config_set(self, mock_pinpoint_client):
        """Test text message sending with configuration set."""
        # Arrange
        destination_phone = '+1234567890'
        originator = '+1987654321'
        message = 'Test message'
        config_set = 'test-config-set'
        expected_message_id = 'test-message-id-123'
        
        mock_pinpoint_client.send_text_message.return_value = {'MessageId': expected_message_id}

        # Act
        result = await send_text_message(
            destination_phone_number=destination_phone,
            originator_identity=originator,
            message=message,
            configuration_set_name=config_set
        )

        # Assert
        assert result == expected_message_id
        mock_pinpoint_client.send_text_message.assert_called_once_with(
            DestinationPhoneNumber=destination_phone,
            OriginationIdentity=originator,
            MessageBody=message,
            ConfigurationSetName=config_set
        )

    async def test_send_text_message_client_error(self, mock_pinpoint_client):
        """Test handling of client errors during text message sending."""
        # Arrange
        destination_phone = '+1234567890'
        originator = '+1987654321'
        message = 'Test message'
        
        mock_pinpoint_client.send_text_message.side_effect = Exception('AWS Client Error')

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await send_text_message(
                destination_phone_number=destination_phone,
                originator_identity=originator,
                message=message
            )
        assert str(exc_info.value) == 'AWS Client Error'
