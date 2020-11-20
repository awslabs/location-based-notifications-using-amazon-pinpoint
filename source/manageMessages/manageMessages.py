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
Lambda function used as an AWS AppSync datasource to handle push notification message templates operations.
Message template is a feature in Amazon Pinpoint, so all requests are handled using the AWS Pinpoint SDK.
"""

import json
import boto3
from botocore.exceptions import ClientError

def handler(event, context):
    """
    Main handler function that get the input messaged passed as parameter along with the operation to be performed.
    The operation is passed via AWS AppSync API, then execute the proper operation.
    """
    print('request: {}'.format(json.dumps(event, indent = 4)))

    pinpoint_client = boto3.client('pinpoint')
    
    message_input = {
      'template_name': event['arguments']['template']
    }

    if 'input' in event['arguments']:
      message_input['service'] = event['arguments']['input']['service']
      message_input['action'] = event['arguments']['input']['action']
      message_input['title'] = event['arguments']['input']['title']
      message_input['body'] = event['arguments']['input']['body']        

    operations = {
      'getMessage': get_message,
      'createMessage': create_message,
      'deleteMessage': delete_message
    }

    response = operations[event['operation']](pinpoint_client, message_input)
    print('response: {}'.format(json.dumps(response, indent = 4)))    
    return response

def get_message(pinpoint_client, message_input):
  """
  Based on a message passed as parameter, it gets a push notification message template 
  in Pinpoint and creates a message Payload to be returned
  """

  try:
    response_get_template = pinpoint_client.get_push_template(
      TemplateName = message_input['template_name']
    ) 

    push_template = response_get_template['PushNotificationTemplateResponse']

    if push_template['APNS']:
      service = 'APNS'
    elif push_template['GCM']:
      service = 'GCM'

    response = {
      'status': 'MESSAGE_OK',
      'message': {
        'service': service,
        'action': push_template[service]['Action'],
        'title': push_template[service]['Title'],
        'body': push_template[service]['Body']
      }
    }  

  except ClientError as ex:      
    response = create_error_payload(
      exception = 'ClientError',
      message = f'Unexpected error: {ex}',
      endpoint_id = ''
    )

  return response

def create_message(pinpoint_client, message_input):
  """
  Based on a message passed as parameter, it creates a push notification 
  message template in Pinpoint
  """

  try:
    template = message_input['template_name']
    service = message_input['service']

    response_create_template = pinpoint_client.create_push_template(
      TemplateName = template,
      PushNotificationTemplateRequest = {
        service: {
          'Action': message_input['action'],
          'Title': message_input['title'],
          'Body': message_input['body']        
        }
      }
    ) 

    response = {
      'status': 'MESSAGE_CREATED',
      'message': f'Personalized {service} push message created for geofence {template}'
    }  

  except ClientError as ex:      
    response = create_error_payload(
      exception = 'ClientError',
      message = f'Unexpected error: {ex}',
      endpoint_id = ''
    )

  return response

def delete_message(pinpoint_client, message_input):
  """
  Based on a message passed as parameter, it deletes a push notification 
  message template in Pinpoint 
  """
  try:
    template = message_input['template_name']

    response_delete_template = pinpoint_client.delete_push_template(
      TemplateName = template
    ) 

    response = {
      'status': 'MESSAGE_DELETED',
      'message': f'Personalized message deleted for geofence {template}'
    }  

  except ClientError as ex:      
    response = create_error_payload(
      exception = 'ClientError',
      message = f'Unexpected error: {ex}',
      endpoint_id = ''
    )

  return response

def create_error_payload(exception, message, endpoint_id):
  """
  Formats an error message to be added in case of failure
  """

  print(f'{exception}: {message}')
  error_payload = {
    'status': 'MESSAGE_ERROR',
    'message': f'{exception}: {message}'        
  }  
  return error_payload 
