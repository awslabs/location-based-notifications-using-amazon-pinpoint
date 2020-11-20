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

"""
Post Confirmation Lambda Trigger function that will be associated with the Cognito User Pool for the application.

Amazon Cognito invokes this trigger after a new user is confirmed, allowing you to send custom messages or to add custom logic. 
"""

import json
import boto3
from botocore.exceptions import ClientError

def handler(event, context):
  """ 
  Gets information about the user, including the username and the type of user its been created, also in which user pool.
  Then, it adds the user in the proper Cognito User Pool group. If it is an administrator user, it will be added into the
  geofence-admin group, otherwise it will add into the geofence-mobile group.
  """

  print('event => : {}'.format(json.dumps(event, indent = 4)))

  userpool_id = event['userPoolId']
  username = event['userName']
  user_type = event['request']['userAttributes']['custom:userType'] if 'custom:userType' in event['request']['userAttributes'] else ''

  if (user_type == 'ADMIN'):
    add_user_to_cognito_group(
      userpool_id =userpool_id,
      username = username,
      group_name = 'geofence-admin'
    )
  else:
    add_user_to_cognito_group(
      userpool_id =userpool_id,
      username = username,
      group_name = 'geofence-mobile'
    )

  return event

def add_user_to_cognito_group(userpool_id, username, group_name):
  """
  Calls the AWS SDK to add a given user into a Cognito User Pool group.
  """

  print(f'Saving {username} to the {group_name} group')
  try:
    cognito_client = boto3.client('cognito-idp')
    response_add_to_group = cognito_client.admin_add_user_to_group(
        UserPoolId = userpool_id,
        Username = username,
        GroupName = group_name
    )
    print('response: {}'.format(json.dumps(response_add_to_group, indent = 4)))
    response = 'SUCESS'  
    
  except ClientError as ex:  
    print(f'ClientError: {ex}')
    response = 'ERROR'
    
  return response
