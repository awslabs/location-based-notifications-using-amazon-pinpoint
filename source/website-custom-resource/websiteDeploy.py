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
Custom resource function to be invoked by the CloudFormation stack in oder to deploy the administrator website.

This function deploys the administrator website into a S3 bucket configured as a website in the Create event. For
the Delete event, the function cleans up the website bucket to be removed by the CloudFormation stack.

This custom resource will be processed only for the Create and Delete events.
"""

import json
import os
import boto3
import zipfile
import cfnResponse 
import mimetypes
from botocore.exceptions import ClientError

s3 = boto3.resource('s3')

def handler(event, context):
  """
  Main handler to control wether to process the Custom Resource in the event of a stack creation or deletion.
  """

  print('request: {}'.format(json.dumps(event, indent = 4)))
  requests = event['ResourceProperties']['Requests'][0]

  origin_bucket = requests['originBucket']
  origin_prefix = requests['originPrefix']
  website_bucket = requests['websiteBucket']
  print('Bucket Origin: ' + origin_bucket)
  print('Bucket Prefix: ' + origin_prefix)
  print('Bucket Target: ' + website_bucket)

  if event['RequestType'] == 'Create':
    print('Creating the Stack...')
    aws_resources = {
      'aws_region': os.environ['REGION'],
      'user_pool_id': requests['userPoolId'],
      'app_client_id': requests['appClientId'],
      'identity_pool_id': requests['identityPoolId'],
      'pinpoint_app_id': requests['pinpointAppId'],
      'appsync_endpoint': requests['appSyncEndpoint']
    }        

    content, content_to_replace = get_website_content_from_origin_bucket(
      event = event,
      context = context,
      origin_bucket = origin_bucket,
      origin_prefix = origin_prefix
    )

    deploy_website_to_target_bucket(
      event = event,
      context = context,
      target_bucket = website_bucket,
      files = content
    )

    replace_aws_resources(
      event = event,
      context = context,
      target_bucket = website_bucket,
      files = content_to_replace,
      aws_resources = aws_resources
    )

    cfnResponse.send(event, context, cfnResponse.SUCCESS, {}, "CustomResourcePhysicalID")

  elif event['RequestType'] == 'Delete':  
    print('Deleting Stack. <No implementation>')
    cfnResponse.send(event, context, cfnResponse.SUCCESS, {}, "CustomResourcePhysicalID")

    '''
    # In case you want to clean up the website bucket during deletion. Default behavior is to
    # keep the s3 bucket and its contents.

    try:
      print('Deleting the Stack...')
      bucket = s3.Bucket(website_bucket)    

      if is_bucket_empty(bucket):
        print(f'Bucket {website_bucket} is empty. No need to clean up')    
      else:
        bucket.objects.all().delete()  
        print (f'Bucket {website_bucket} was cleaned up with success')  

      cfnResponse.send(event, context, cfnResponse.SUCCESS, {}, "CustomResourcePhysicalID")

    except ClientError as ex:     
      print(f'Target Bucket {website_bucket} with error: {ex}')    
      cfnResponse.send(event, context, cfnResponse.FAILED, {}, "CustomResourcePhysicalID")  
    '''   

  else:
    print('Updating Stack. <No implementation>')   
    cfnResponse.send(event, context, cfnResponse.SUCCESS, {}, "CustomResourcePhysicalID") 

def replace_aws_resources(event, context, target_bucket, files, aws_resources):
  """
  Replace all placeholders at deployment time with the newly created resources. Then sends the files
  to the S3 website bucket
  """

  print(f'Setting up AWS resources to the admin website')
  
  try:    
    for webSiteFile in files:
      with open(webSiteFile) as f:
        content = f.read()
      
      content = content.replace("REPLACE_AWS_REGION", aws_resources['aws_region'])
      content = content.replace("REPLACE_USER_POOL_ID", aws_resources['user_pool_id'])
      content = content.replace("REPLACE_APP_CLIENT_ID", aws_resources['app_client_id'])
      content = content.replace("REPLACE_IDENTITY_POOL_ID", aws_resources['identity_pool_id'])
      content = content.replace("REPLACE_PINPOINT_APP_ID", aws_resources['pinpoint_app_id'])
      content = content.replace("REPLACE_APPSYNC_ENDPOINT", aws_resources['appsync_endpoint'])

      encoded_string = content.encode("utf-8")      
      website_key = os.path.relpath(webSiteFile, '/tmp/website-contents')    
      guessed_mime_type = mimetypes.guess_type(webSiteFile)
      
      if website_key.startswith('../'):
        file_key = website_key[len('../'):]
      else:
        file_key = website_key
      
      if guessed_mime_type is None:
        raise Exception("Failed to guess mimetype")
        
      mime_type = guessed_mime_type[0]  
      
      if mime_type is None:
        mime_type = 'binary/octet-stream'
        
      s3.Bucket(target_bucket).put_object(
        Key=file_key, 
        Body=encoded_string,
        ContentType=mime_type
      )

      print(f'{file_key} uploaded to {target_bucket}')

    print(f'AWS Resources set and deployed successfully to {target_bucket} bucket')  
  except ClientError as ex:     
    print(f'Target Bucket {target_bucket} with error: {ex}')  
    cfnResponse.send(event, context, cfnResponse.FAILED, {}, "CustomResourcePhysicalID")  

def deploy_website_to_target_bucket(event, context, target_bucket, files):
  """
  Deploys the website files into the S3 website bucket
  """

  print(f'Starting admin website deployment to {target_bucket} bucket')

  try:    
    for webSiteFile in files:
      with open(webSiteFile) as f:
        content = f.read()

      encoded_string = content.encode("utf-8")
      website_key = os.path.relpath(webSiteFile, '/tmp/website-contents')   
      guessed_mime_type = mimetypes.guess_type(webSiteFile)
      
      if website_key.startswith('../'):
        file_key = website_key[len('../'):]
      else:
        file_key = website_key
        
      print('Key being uploaded to S3: ' + file_key)

      if guessed_mime_type is None:
        raise Exception("Failed to guess mimetype")
        
      mime_type = guessed_mime_type[0]  
      
      if mime_type is None:
        mime_type = 'binary/octet-stream'
      
      s3.Bucket(target_bucket).put_object(
        Key=file_key, 
        Body=encoded_string,
        ContentType=mime_type
      )

      print(f'{file_key} uploaded to {target_bucket}')

    print(f'Admin website deployed successfully to {target_bucket} bucket')  
  except ClientError as ex:     
    print(f'Target Bucket {target_bucket} with error: {ex}')    
    cfnResponse.send(event, context, cfnResponse.FAILED, {}, "CustomResourcePhysicalID")  
    
def get_website_content_from_origin_bucket(event, context, origin_bucket, origin_prefix):
  """
  Gets the website raw content and stores in the Lambda tmp directory to be processed
  """

  print(f'Getting website files from {origin_bucket} bucket')

  try:
    key = 'website-contents.zip'
    full_key = origin_prefix + key
    tmp_dir = '/tmp/'
    local_file_name = tmp_dir + key

    s3.Bucket(origin_bucket).download_file(full_key, local_file_name)
    print(f'File {key} downloaded to {local_file_name}')

    print(f'Extracting file {key} to {tmp_dir}')
    with zipfile.ZipFile(local_file_name, 'r') as zip_ref:
      zip_ref.extractall(tmp_dir)

    print(f'Deleting {local_file_name}')
    os.remove(local_file_name)

    files = []
    files_to_replace = []

    for r, d, f in os.walk(tmp_dir):
      for file in f:
        if file.startswith('main') and all(x in file for x in 'js') and '.ico' not in file:
          files_to_replace.append(os.path.join(r, file))  
        elif '.ico' not in file:
          files.append(os.path.join(r, file))
    
    return files, files_to_replace
      
  except ClientError as ex:     
    print(f'Origin Bucket {origin_bucket} with error: {ex}')  
    cfnResponse.send(event, context, cfnResponse.FAILED, {}, "CustomResourcePhysicalID")  

def is_bucket_empty(bucket):
  """
  Returns true if the S3 website bucket is empty, false otherwise
  """

  total_obj = len(list(bucket.objects.all()))
  return total_obj == 0

def is_bucket_exist(bucket):
  """
  Returns true if the S3 website bucket exists, false otherwise
  """

  if bucket.creation_date:
    return True
  else:
    return False    
