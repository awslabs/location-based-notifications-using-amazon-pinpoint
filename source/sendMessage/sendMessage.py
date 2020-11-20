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
Lambda function used as an AWS AppSync datasource to send location based push notifications
based on the geofence that users passed within.
"""

import json
import uuid 
import os
import time
import boto3
from botocore.exceptions import ClientError

def handler(event, context):
    """
    Proccess all scenarios to send a push notification to a given user that passed in a given geofence.

    It handles APNS and FCM/GCM push notifications.

    First gets the endpoint based on the user id.

    Extracts attributes data from the endpoint to be used in the processing logic, attributes such as:
    the geofences the user already passed within
    the current status to check if the user is a premium user in all geofences he passed into

    Gets the proper message template checking the channel type and if the user is a premium user for the specific geofence.

    With the proper message template, it send the push notification to the endpoint address

    Updates the number of visits a geofence has in the DynamoDB table

    Updates the endpoint attributes with increasing the number of visits in a given geofence and checking/updating 
    if the endpoint has become a premium user

    Creates a return payload. In case of any failure, a error paylod is created
    """

    print('request: {}'.format(json.dumps(event, indent = 4)))

    dbb_table_name = os.environ['DBB_TABLE_NAME']
    pinpoint_application_id = event['arguments']['input']['applicationId']
    geofence_id = event['arguments']['input']['geofenceId']
    user_id = event['arguments']['input']['userId']

    try:
      pinpoint_client = boto3.client('pinpoint')
      dbb_client = boto3.client('dynamodb')

      response_endpoint = pinpoint_client.get_user_endpoints(
        ApplicationId=pinpoint_application_id,
        UserId=user_id
      ) 

      response_endpoint_items = response_endpoint['EndpointsResponse']['Item']

      if (len(response_endpoint_items) >= 1):
        endpoint = response_endpoint_items[0]
        endpoint_id = endpoint['Id'] 
        endpoint_channel_type = endpoint['ChannelType'] 
        endpoint_address = endpoint['Address']
        endpoint_attribute_geofences = endpoint['Attributes']['geofences'] if 'geofences' in endpoint['Attributes'] else []
        endpoint_attribute_premium = endpoint['Attributes']['premiumUser'] if 'premiumUser' in endpoint['Attributes'] else []

        
        if (is_user_premium(endpoint_attribute_premium, geofence_id)):
          response_message_template = pinpoint_client.get_push_template(
            TemplateName = f'{geofence_id}-PREMIUM'
          )
        else:           
          response_message_template = pinpoint_client.get_push_template(
              TemplateName=geofence_id        
          )     
            
        message_template_apns = response_message_template['PushNotificationTemplateResponse']['APNS'] if 'APNS' in response_message_template['PushNotificationTemplateResponse'] else []
        message_template_gcm = response_message_template['PushNotificationTemplateResponse']['GCM'] if 'GCM' in response_message_template['PushNotificationTemplateResponse'] else []
        message_template_default = response_message_template['PushNotificationTemplateResponse']['Default'] if 'Default' in response_message_template['PushNotificationTemplateResponse'] else []

        if (endpoint_channel_type == 'APNS'):
          if (message_template_apns):
            message_template_title = message_template_apns['Title']
            message_template_body = message_template_apns['Body']
          elif (message_template_gcm):
            raise ValueError(f'APNS template not found for geofence ID {geofence_id}')  
          else:
            message_template_title = message_template_default['Title']
            message_template_body = message_template_default['Body']
        elif (endpoint_channel_type == 'GCM'):
          if (message_template_gcm):
            message_template_title = message_template_gcm['Title']
            message_template_body = message_template_gcm['Body']
          elif (message_template_apns):
            raise ValueError(f'GCM template not found for geofence ID {geofence_id}')  
          else:
            message_template_title = message_template_default['Title']
            message_template_body = message_template_default['Body']

        message_recipient = {
          'token': endpoint_address,
          'service': endpoint_channel_type
        }
        
        response_send_message = pinpoint_client.send_messages(
          ApplicationId = pinpoint_application_id,
          MessageRequest = create_message_request(
            service = endpoint_channel_type, 
            token = endpoint_address, 
            title = message_template_title, 
            body = message_template_body
          )
        )
        
        message_delivery_status = response_send_message['MessageResponse']['Result'][message_recipient["token"]]['DeliveryStatus']

        if (message_delivery_status == "SUCCESSFUL"):
          response_dbb_update = dbb_client.update_item(
            TableName = dbb_table_name,
            Key = {
              'id': {'S': geofence_id}
            },
            UpdateExpression = 'set visits = visits + :incr',
            ExpressionAttributeValues = {
              ':incr': {'N': '1'}
            },
            ReturnValues = 'UPDATED_NEW'
          )

          if (response_dbb_update['ResponseMetadata']['HTTPStatusCode'] == 200):
            response_update_endpoint = pinpoint_client.update_endpoint(
              ApplicationId = pinpoint_application_id,
              EndpointId = endpoint_id,
              EndpointRequest = {
                'Attributes': {
                  'premiumUser': update_premium_user_attribute_if_5_visits(endpoint_attribute_premium, endpoint_attribute_geofences, geofence_id),
                  'geofences': update_geofences_attribute(endpoint_attribute_geofences, geofence_id)
                }
              }
            )

            if (response_update_endpoint['ResponseMetadata']['HTTPStatusCode'] == 202):
              response = {
                'status': 'MESSAGE_SENT',
                'message': f'Message sent successfully to user ID {user_id} from the geofence ID {geofence_id}',
                'endpointId': endpoint_id
              }  
            
            else:
              response = create_error_payload(
                exception = 'UpdateEndpointError',
                message = f'Error while updating endpoint ID {endpoint_id}',
                endpoint_id = endpoint_id
              )

          else:
            response = create_error_payload(
            exception = 'DynamoDBUpdateError',
            message = f'Error while updating the number of visits for geofence ID {geofence_id}',
            endpoint_id = endpoint_id
          )

        else:
          response = create_error_payload(
            exception = message_delivery_status,
            message = response_send_message['MessageResponse']['Result'][message_recipient["token"]]['StatusMessage'],
            endpoint_id = endpoint_id
          )

      else:
        response = create_error_payload(
          exception = 'NotFoundException',
          message = f'No endpoint found for the User ID {user_id}',
          endpoint_id = ''
        )

    except ValueError as ex:
      response = create_error_payload(
        exception = 'ValueError',
        message = str(ex),
        endpoint_id = ''
      )

    except pinpoint_client.exceptions.NotFoundException as ex:
      response = create_error_payload(
        exception = f'NotFoundException: {ex.operation_name}',
        message = str(ex),
        endpoint_id = ''
      )

    except ClientError as ex:      
      response = create_error_payload(
        exception = 'ClientError',
        message = f'Unexpected error: {ex}',
        endpoint_id = ''
      )
  
    print('response: {}'.format(json.dumps(response, indent = 4)))    
    return response

def update_geofences_attribute(geofences_list, current_geofence):
  """
  Updates the edpoint geofence list by adding the timestamp of the last visit a user had  and the number of visits
  in that geofence.
  """

  element_not_exist = False

  if (not geofences_list):
    geofences_list.append(f'{current_geofence}|{int(time.time())}|1')
  else:   
    for geofence in geofences_list:
      if (geofence.startswith(current_geofence)):        
        geofence_data = geofence.split('|')
        geofences_list.remove(geofence)
        geofences_list.append(f'{current_geofence}|{int(time.time())}|{int(geofence_data[2]) + 1 }')
        element_not_exist = True
        break
      
    if (not element_not_exist):
      geofences_list.append(f'{current_geofence}|{int(time.time())}|1')
    
  return geofences_list

def update_premium_user_attribute_if_5_visits(premium_user_list, geofences_list, current_geofence):
  """
  Updates the status of the endpoint in the passed geofence to transform the user in a PREMIUM user
  """
  element_not_exist = False
  
  if (not geofences_list):
    premium_user_list.append(f'{current_geofence}|NO')
  else:
    for geofence in geofences_list:      
      if (geofence.startswith(current_geofence)):  
        geofence_data = geofence.split('|')
        current_number_of_visits = (int(geofence_data[2]) + 1)
        element_not_exist = True

        if (current_number_of_visits >= 5):
          if f'{current_geofence}|NO' in premium_user_list: premium_user_list.remove(f'{current_geofence}|NO')
          if f'{current_geofence}|YES' in premium_user_list: premium_user_list.remove(f'{current_geofence}|YES')
          premium_user_list.append(f'{current_geofence}|YES')          
          break

    if (not element_not_exist):
      premium_user_list.append(f'{current_geofence}|NO')    
    
  return premium_user_list

def is_user_premium(premium_user_list, current_geofence):
  """
  Returns true if the user is a premium user, false otherwise
  """
  is_premium = False

  if (premium_user_list):
    for premium_user in premium_user_list:      
      premium_data = premium_user.split('|')
      geofence_id = premium_data[0]
      premium = premium_data[1]

      if (geofence_id == current_geofence and premium == 'YES'):        
        is_premium = True
        break

  return is_premium  

def create_message_request(service, token, title, body):
  """
  Dynamically creates the request paylod to send push notifications based on the input provided
  """

  action = 'OPEN_APP'
  priority = 'normal'
  silent = False  
  ttl = 30
  
  if service == "GCM":
    message_request = {
      'Addresses': {
        token: {
          'ChannelType': 'GCM'
        }
      },
      'MessageConfiguration': {
        'GCMMessage': {
          'Action': action,
          'Body': body,
          'Priority' : priority,
          'SilentPush': silent,
          'Title': title,
          'TimeToLive': ttl          
        }
      }
    }
  elif service == "APNS":
    message_request = {
      'Addresses': {
        token: {
          'ChannelType': 'APNS'
        }
      },
      'MessageConfiguration': {
        'APNSMessage': {
          'Action': action,
          'Body': body,
          'Priority' : priority,
          'SilentPush': silent,
          'Title': title,
          'TimeToLive': ttl          
        }
      }
    }
    
  else:
    message_request = None

  return message_request

def create_error_payload(exception, message, endpoint_id):
  """
  Creates an error payload to be send as a response in case of failure
  """

  print(f'{exception}: {message}')
  error_payload = {
    'status': 'MESSAGE_NOT_SENT',
    'endpointId': endpoint_id if endpoint_id else 'NO_ENDPOINT_ID',
    'message': f'{exception}: {message}'        
  }  
  return error_payload 
