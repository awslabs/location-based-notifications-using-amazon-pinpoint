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
from moto import mock_cognitoidp

import boto3
import uuid
import os
import json
import random
import cognitoPosConfirmation

@mock_cognitoidp
class TestCognitoPosConfirmation(unittest.TestCase):  
  """
  Test class for the CognitoPosConfirmation function 
  """  
  
  def test_cognito_pos_confirmation_add_mobile_user_with_succes(self):
    """
    Test when cognito is able to add a mobile user into the geofence-mobile group
    """    

    user_pool_name = 'sample-mock-userpool'
    mobile_username = 'mobile_user'
    role_arn = "arn:aws:iam:::role/my-iam-role"

    conn = boto3.client("cognito-idp")
    
    user_pool_id = conn.create_user_pool(PoolName=user_pool_name)["UserPool"]["Id"]

    mobile_group_name = 'geofence-mobile'
    role_arn = "arn:aws:iam:::role/my-iam-role"

    result_create_group = conn.create_group(
      GroupName=mobile_group_name,
      UserPoolId=user_pool_id,
      Description=str(uuid.uuid4()),
      RoleArn=role_arn,
      Precedence=random.randint(0, 100000),
    )    

    conn.admin_create_user(UserPoolId=user_pool_id, Username=mobile_username)

    event = {
      'version': '1',
      'region': 'us-east-1',
      'userPoolId': user_pool_id,
      'userName': mobile_username,
      'callerContext': {
          'awsSdkVersion': 'aws-sdk-unknown-unknown',
          'clientId': 'some_client_id'
      },
      'triggerSource': 'PostConfirmation_ConfirmSignUp',
      'request': {
          'userAttributes': {
              'sub': 'some_user_sub',
              'cognito:user_status': 'CONFIRMED',
              'email_verified': 'true',
              'email': 'someuser@somemail.com'
          }
      },
      'response': {}       
    }

    response = cognitoPosConfirmation.handler(event, None)

    self.assertTrue(response)
    self.assertEqual(response['userPoolId'], user_pool_id)
    self.assertFalse(response['response'])

  def test_cognito_pos_confirmation_add_admin_user_with_succes(self):
    """
    Test when cognito is able to add an admin user into the geofence-admin group
    """    

    user_pool_name = 'sample-mock-userpool'
    admin_username = 'admin_user'
    role_arn = "arn:aws:iam:::role/my-iam-role"

    conn = boto3.client("cognito-idp")

    user_pool_id = conn.create_user_pool(PoolName=user_pool_name)["UserPool"]["Id"]

    admin_group_name = 'geofence-admin'
    role_arn = "arn:aws:iam:::role/my-iam-role"

    result_create_group = conn.create_group(
      GroupName=admin_group_name,
      UserPoolId=user_pool_id,
      Description=str(uuid.uuid4()),
      RoleArn=role_arn,
      Precedence=random.randint(0, 100000),
    )

    conn.admin_create_user(UserPoolId=user_pool_id, Username=admin_username)

    event = {
      'version': '1',
      'region': 'us-east-1',
      'userPoolId': user_pool_id,
      'userName': admin_username,
      'callerContext': {
          'awsSdkVersion': 'aws-sdk-unknown-unknown',
          'clientId': 'some_client_id'
      },
      'triggerSource': 'PostConfirmation_ConfirmSignUp',
      'request': {
          'userAttributes': {
              'sub': 'some_user_sub',
              'cognito:user_status': 'CONFIRMED',
              'email_verified': 'true',
              'email': 'someuser@somemail.com',
              'custom:userType': 'ADMIN'
          }
      },
      'response': {}       
    }

    response = cognitoPosConfirmation.handler(event, None)

    self.assertTrue(response)
    self.assertEqual(response['userPoolId'], user_pool_id)
    self.assertTrue(response['request']['userAttributes']['custom:userType'])
    self.assertEqual(response['request']['userAttributes']['custom:userType'], 'ADMIN')
    self.assertFalse(response['response'])  

if __name__ == '__main__':
    unittest.main()  