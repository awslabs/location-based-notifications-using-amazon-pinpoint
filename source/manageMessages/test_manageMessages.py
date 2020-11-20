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
import manageMessages

class TestManageMessages(unittest.TestCase):  
  """
  Test class for the ManageMessages function 
  """  
  
  @patch('boto3.client')
  def test_create_message_with_succes(self, mock_client):
    """
    Test when the lambda is able to create a message template on Pinpoint
    """    

    event = {
      'operation': 'createMessage',  
      'arguments': {
        'template': 'my-sample-geofence-id',
        'input': {
          'service': 'APNS',
          'action': 'OPEN_APP',
          'title': 'Sample Title',
          'body': 'This is a sample body'
        }
      }
    }

    response = {
        "Arn": f'arn:aws:mobiletargeting:eus-east-1:SOME_ACCOUNT_ID:templates/my-sample-geofence-id/PUSH',
        "RequestID": "some-request-id",
        "Message": 'some message'          
    }

    mock_client().create_push_template.return_value = response
    response = manageMessages.handler(event, None)

    self.assertTrue(response)
    self.assertEqual(response['status'], 'MESSAGE_CREATED')  

  @patch('boto3.client')
  def test_get_apns_message_with_succes(self, mock_client):
    """
    Test when the lambda is able to get an APNS message template on Pinpoint
    """    

    event = {
      'operation': 'getMessage',  
      'arguments': {
        'template': 'my-sample-geofence-id',
      }
    }

    response = {
        "PushNotificationTemplateResponse": {
          'APNS': {
            'Action': 'OPEN_APP',
            'Title': 'Sample Title',
            'Body': 'This is a sample body'
          }
        }
    }

    mock_client().get_push_template.return_value = response
    response = manageMessages.handler(event, None)

    self.assertTrue(response)
    self.assertEqual(response['status'], 'MESSAGE_OK')
    self.assertEqual(response['message']['service'], 'APNS')  

  @patch('boto3.client')
  def test_delete_message_with_succes(self, mock_client):
    """
    Test when the lambda is able to delete a message template on Pinpoint
    """    

    event = {
      'operation': 'deleteMessage',  
      'arguments': {
        'template': 'my-sample-geofence-id',
      }
    }

    response = {
      "Arn": f'arn:aws:mobiletargeting:eus-east-1:SOME_ACCOUNT_ID:templates/my-sample-geofence-id/PUSH',
      "RequestID": "some-request-id",
      "Message": 'some message'          
    }

    mock_client().delete_push_template.return_value = response
    response = manageMessages.handler(event, None)

    self.assertTrue(response)
    self.assertEqual(response['status'], 'MESSAGE_DELETED')       

if __name__ == '__main__':
    unittest.main()  