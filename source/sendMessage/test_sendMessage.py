"""
  Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved

  Licensed under the MIT No Attribution License (MIT-0) (the ‘License’). You may not use this file except in compliance
  with the License. A copy of the License is located at

      https://opensource.org/licenses/MIT-0

  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files 
  (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, 
  publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so.
  THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR 
  ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH 
  THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.    
"""

import unittest
from unittest.mock import Mock, patch

import boto3
import uuid
import os
import json
import random
import sendMessage

class TestSendMessage(unittest.TestCase):  
  """
  Test class for the SendMessage function 
  """  

  ENV_DBB_TABLE_NAME = 'DBB_TABLE_NAME'
  DDB_TABLE_NAME = 'geofence-ddb-table'

  def setUp(self):
    """
    Setting up the test case
    """
    os.environ[TestSendMessage.ENV_DBB_TABLE_NAME] = TestSendMessage.DDB_TABLE_NAME

  @patch('boto3.client')
  def test_send_message_with_succes(self, mock_client):
    """
    Test when the lambda is able to send a push notification
    """    

    event = {
      'arguments': {
        'input': {
          'applicationId': 'pinpoint-app-id',
          'geofenceId': 'geofence-id',
          'userId': 'user-id'
        }
      }
    }

    response_endpoint = {
      'EndpointsResponse': {
        'Item': [{
          'Id': 'endpoint-id',
          'ChannelType': 'APNS',
          'Address': 'endpoint-address',
          'Attributes': []
        }]
      }
    }

    response_template = {
      "PushNotificationTemplateResponse": {
        'APNS': {
          'Action': 'OPEN_APP',
          'Title': 'Sample Title',
          'Body': 'This is a sample body'
        }
      }
    }

    response_send_message = {
      "MessageResponse": {
        'Result': {
          'endpoint-address': {
            'DeliveryStatus': 'SUCCESSFUL'
          }
        }
      }
    }

    response_ddb_update = {
      "ResponseMetadata": {
        'HTTPStatusCode': 200
      }
    }

    response_update_endpoint = {
      "ResponseMetadata": {
        'HTTPStatusCode': 202
      }
    }

    mock_client().get_user_endpoints.return_value = response_endpoint
    mock_client().get_push_template.return_value = response_template
    mock_client().send_messages.return_value = response_send_message
    mock_client().update_item.return_value = response_ddb_update
    mock_client().update_endpoint.return_value = response_update_endpoint

    response = sendMessage.handler(event, None)

    self.assertTrue(response)
    self.assertEqual(response['status'],'MESSAGE_SENT')
    self.assertEqual(response['endpointId'],'endpoint-id')      

if __name__ == '__main__':
    unittest.main()    