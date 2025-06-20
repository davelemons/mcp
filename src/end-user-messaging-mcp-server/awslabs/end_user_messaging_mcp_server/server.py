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

"""awslabs end-user-messaging MCP Server implementation."""

import boto3
import os
from loguru import logger
from mcp.server.fastmcp import FastMCP
from pydantic import Field


# Initialize client
aws_region: str = os.environ.get('AWS_REGION', 'us-east-1')

try:
    if aws_profile := os.environ.get('AWS_PROFILE'):
        pinpoint_client = boto3.Session(profile_name=aws_profile, region_name=aws_region).client(
            'pinpoint-sms-voice-v2'
        )
    else:
        pinpoint_client = boto3.Session(region_name=aws_region).client('pinpoint-sms-voice-v2')
except Exception as e:
    logger.error(f'Error creating pinpoint-sms-voice-v2 client: {str(e)}')
    raise



mcp = FastMCP(
    'awslabs.end-user-messaging-mcp-server',
    instructions='Instructions for using this end-user-messaging MCP server. This can be used by clients to improve the LLM'
    's understanding of available tools, resources, etc. It can be thought of like a '
    'hint'
    ' to the model. For example, this information MAY be added to the system prompt. Important to be clear, direct, and detailed.',
    dependencies=[
        'pydantic',
        'loguru',
    ],
)


@mcp.tool(name='SendTextMessage')
async def send_text_message(
    destination_phone_number: str = Field(
        ...,
        description='The phone number to send the message to in E.164 Format',
    ),
    originator_identity: str = Field(
        ...,
        description='End User Messaging Origination Identity in E.164 Format',
    ),
    message: str = Field(
        ...,
        description='The message to send to the user',
    ),
    configuration_set_name: Optional[str] = Field(
        default=None,
        description='The name of the configuration set to use for the message',
    ),
) -> str:
    """SendTextMessage tool implementation.

    Parameters:
        destination_phone_number (str): The phone number to send the message to in E.164 Format.
        originator_identity (str): End User Messaging Origination Identity.
        configuration_set_name (str): The name of the configuration set to use for the message.
        message (str): The message to send to the user.

    Returns:
        The messageId of the sent message.
    """

    if not sms_origination_identity := os.environ.get('SMS_ORIGINATION_IDENTITY'):
        raise Exception('SMS_ORIGINATION_IDENTITY is not set')

    create_params = {
        'DestinationPhoneNumber': destination_phone_number,
        'OriginationIdentity': sms_origination_identity,
        'MessageBody': message,
    }

    if configuration_set_name := os.environ.get('CONFIGURATION_SET_NAME'):
        create_params['ConfigurationSetName'] = configuration_set_name

    response = pinpoint_client.send_text_message(**create_params)
    message_id = response['MessageId']
    return message_id


def main():
    """Run the MCP server with CLI argument support."""
    logger.trace('A trace message.')
    logger.debug('A debug message.')
    logger.info('An info message.')
    logger.success('A success message.')
    logger.warning('A warning message.')
    logger.error('An error message.')
    logger.critical('A critical message.')

    mcp.run()


if __name__ == '__main__':
    main()
