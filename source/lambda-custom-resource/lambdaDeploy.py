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
Custom resource function to be invoked by the CloudFormation stack in oder to create deploy a Lambda@Edge function.

This function creates a Lambda function in the us-east-1 region to be deployed together with CloudFront. It will add security headers to the 
administrator website.

This custom resource will be processed only for the Create and Delete events.
"""

import json
import boto3
import time
import cfnResponse 
from botocore.exceptions import ClientError
import zipfile

lambda_client = boto3.client('lambda', region_name='us-east-1')
ssm_client = boto3.client('ssm', region_name='us-east-1')
iam_client = boto3.client('iam')
client_sts = boto3.client('sts')

function_code = '''
/*******************************************************************************************************************************************
*  Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved                                                                  *
*                                                                                                                                          *
*  Licensed under the MIT No Attribution License (MIT-0) (the ‘License’). You may not use this file except in compliance                   *
*  with the License. A copy of the License is located at                                                                                   *
*                                                                                                                                          *
*      https://opensource.org/licenses/MIT-0                                                                                               *
*                                                                                                                                          *
*  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files        *
*  (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge,     *
*  publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so.  *
*  THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF      *
*  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR *
*  ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH  * 
*  THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                                                                              *
*******************************************************************************************************************************************/

'use strict';

const AWS = require('aws-sdk')

AWS.config.update({
  region: 'us-east-1'
})

const parameterStore = new AWS.SSM()

const getParam = param => {
  return new Promise((res, rej) => {
    parameterStore.getParameter({
      Name: param
    }, (err, data) => {
        if (err) {
          return rej(err)
        }
        return res(data)
    })
  })
}

exports.handler = async (event, context, callback) => {
    const regionSSM = await getParam('REPLACE_REGION_SSM');
    const region = regionSSM.Parameter.Value;
    
    const request = event.Records[0].cf.request;
    const response = event.Records[0].cf.response;
    const headers = response.headers;
    const origin = request.origin.s3.domainName;
    
    let bucketName = origin.substring(0, origin.indexOf(".")) + ".s3.amazonaws.com";
    let secPolicyPlaceholder = "default-src 'none'; connect-src 'self' https://cognito-idp.<AWS_REGION>.amazonaws.com/ https://cognito-identity.<AWS_REGION>.amazonaws.com/ REPLACE_APPSYNC_ENDPOINT <ORIGIN_BUCKET>; font-src 'self' data: <ORIGIN_BUCKET>; frame-src 'self' <ORIGIN_BUCKET>; img-src 'self' data: https:; media-src 'self'; script-src 'self' 'unsafe-inline' <ORIGIN_BUCKET> data:; style-src 'self' 'unsafe-inline' <ORIGIN_BUCKET>; object-src 'none'";
    let secPolicyHeader = secPolicyPlaceholder.split("<ORIGIN_BUCKET>").join(bucketName);
    secPolicyHeader = secPolicyHeader.split("<AWS_REGION>").join(region);

    headers['strict-transport-security'] = [{
        key: 'Strict-Transport-Security', 
        value: 'max-age=63072000; includeSubdomains; preload'        
    }]; 
    
    headers['x-content-type-options'] = [{
        key: 'X-Content-Type-Options', 
        value: 'nosniff'        
    }]; 
    
    headers['x-frame-options'] = [{
        key: 'X-Frame-Options', 
        value: 'DENY'        
    }]; 
    
    headers['x-xss-protection'] = [{
        key: 'X-XSS-Protection', 
        value: '1; mode=block'        
    }]; 
    
    headers['referrer-policy'] = [{
        key: 'Referrer-Policy', 
        value: 'same-origin'        
    }]; 
    
    headers['content-security-policy'] = [{
        key: 'Content-Security-Policy', 
        value: secPolicyHeader        
    }]; 
    
    callback(null, response);
};
'''

def handler(event, context):
  """
  Main handler to control wether to process the Custom Resource in the event of a stack creation or deletion.
  """

  print('request: {}'.format(json.dumps(event, indent = 4)))
  requests = event['ResourceProperties']['Requests'][0]

  stack_parameters = {
    'aws_region': requests['awsRegion'],
    'lambda_name': requests['lambdaName'],
    'ssm_parameter_name': requests['ssmParamName'],
    'role_name': requests['lambdaRoleName'],
    'policy_name': requests['lambdaPolicyName'],
    'account_id': client_sts.get_caller_identity()['Account'],
    'app_sync_endpoint': requests['appSyncEndpoint']
  }

  if event['RequestType'] == 'Create':
    print('Creating the Stack...')
    handle_create(
      event = event, 
      context = context, 
      stack_parameters = stack_parameters
    )

  elif event['RequestType'] == 'Delete':  
    print('Deleting the Stack...')
    handle_delete(
      event = event, 
      context = context, 
      stack_parameters = stack_parameters
    )

  else:
    print('Updating Stack. <No implementation>')
    cfnResponse.send(event, context, cfnResponse.SUCCESS, {}, "LambdaEdgeCustomResourcePhysicalID")

def handle_create(event, context, stack_parameters):
  """
  Creates a lambda function and all the resources related.
  """

  try:
    aws_region = stack_parameters['aws_region']
    lambda_name = stack_parameters['lambda_name']
    ssm_parameter_name = stack_parameters['ssm_parameter_name']
    account_id = stack_parameters['account_id']   
    role_name = stack_parameters['role_name']
    policy_name = stack_parameters['policy_name']
    app_sync_endpoint = stack_parameters['app_sync_endpoint']

    response_ssm = ssm_client.put_parameter(
        Name = ssm_parameter_name,
        Value = aws_region,
        Type = 'String'
    )
    
    trust_policy={
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Principal": {
            "Service": [
              "edgelambda.amazonaws.com",
              "lambda.amazonaws.com"
            ]
          },
          "Action": "sts:AssumeRole"
        }
      ]
    }
    
    managed_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowSSMParameter",
                "Effect": "Allow",
                "Action": "ssm:GetParameter*",
                "Resource": f'arn:aws:ssm:us-east-1:{account_id}:parameter/{ssm_parameter_name}*'
            },
            {
                "Effect": "Allow",
                "Action": "logs:CreateLogGroup",
                "Resource": f'arn:aws:logs:us-east-1:{account_id}:*'
            },
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": [
                    f'arn:aws:logs:us-east-1:{account_id}:log-group:/aws/lambda/{lambda_name}:*'
                ]
            }
        ]
    }
    
    response_iam = iam_client.create_role(
        RoleName = role_name,
        Path = '/service-role/',
        AssumeRolePolicyDocument = json.dumps(trust_policy),
        Description = 'Execution role for Lambda edge function'
    )
    
    response = iam_client.create_policy(
      PolicyName = policy_name,
      PolicyDocument = json.dumps(managed_policy)
    )
    
    iam_client.attach_role_policy(
        PolicyArn = f'arn:aws:iam::{account_id}:policy/{policy_name}',
        RoleName = role_name
    )
    
    time.sleep(10)

    function_code_replaced = function_code.replace("REPLACE_REGION_SSM", ssm_parameter_name)
    function_code_replaced = function_code_replaced.replace("REPLACE_APPSYNC_ENDPOINT", app_sync_endpoint) 

    zf = zipfile.ZipFile('/tmp/function.zip', mode='w', compression=zipfile.ZIP_DEFLATED)
    info = zipfile.ZipInfo('index.js')
    info.external_attr = 0o664 << 16
    zf.writestr(info, function_code_replaced)
    zf.close()
    
    with open('/tmp/function.zip', 'rb') as f: 
      code = f.read()
    
    response = lambda_client.create_function(
        FunctionName = lambda_name,
        Runtime = "nodejs12.x",
        Role = f'arn:aws:iam::{account_id}:role/service-role/{role_name}',
        Handler = "index.handler",
        Code = { 
          'ZipFile': code
        }
    )
    
    response_lambda = lambda_client.publish_version(
        FunctionName = lambda_name
    )    

    version_arn = response_lambda['FunctionArn']
    print(f'Lambda {version_arn} created properly in us-east-1 region')  

    lambda_arn = {
      'lambdaArn': version_arn
    }

    cfnResponse.send(event, context, cfnResponse.SUCCESS, lambda_arn, "LambdaEdgeCustomResourcePhysicalID")

  except ClientError as ex:     
    print(f'Error deploying Lambda Edge in us-east-1 with error: {ex}')  
    cfnResponse.send(event, context, cfnResponse.FAILED, {}, "LambdaEdgeCustomResourcePhysicalID")

def handle_delete(event, context, stack_parameters):
  """
  When the stack is being deleted, this function will delete all resources previously created by this function in the Create event.
  """

  try:
    aws_region = stack_parameters['aws_region']
    lambda_name = stack_parameters['lambda_name']
    ssm_parameter_name = stack_parameters['ssm_parameter_name']
    account_id = stack_parameters['account_id']   
    role_name = stack_parameters['role_name']
    policy_name = stack_parameters['policy_name']
    
    response_detach = iam_client.detach_role_policy(
        RoleName = role_name,
        PolicyArn = f'arn:aws:iam::{account_id}:policy/{policy_name}'   
    )

    if response_detach['ResponseMetadata']['HTTPStatusCode'] == 200:
      response_role = iam_client.delete_role(
        RoleName = role_name
      )

      if response_role['ResponseMetadata']['HTTPStatusCode'] == 200:
        response_policy = iam_client.delete_policy(
          PolicyArn = f'arn:aws:iam::{account_id}:policy/{policy_name}'   
        )

        if response_policy['ResponseMetadata']['HTTPStatusCode'] == 200:
          response_ssm = ssm_client.delete_parameter(
            Name = ssm_parameter_name
          )  

          if response_ssm['ResponseMetadata']['HTTPStatusCode'] == 200:
            cfnResponse.send(event, context, cfnResponse.SUCCESS, {}, "LambdaEdgeCustomResourcePhysicalID")

          else:
            cfnResponse.send(event, context, cfnResponse.FAILED, {}, "LambdaEdgeCustomResourcePhysicalID")              
        else:
          cfnResponse.send(event, context, cfnResponse.FAILED, {}, "LambdaEdgeCustomResourcePhysicalID")    
      else:
        cfnResponse.send(event, context, cfnResponse.FAILED, {}, "LambdaEdgeCustomResourcePhysicalID")    
    else:
      cfnResponse.send(event, context, cfnResponse.FAILED, {}, "LambdaEdgeCustomResourcePhysicalID")       

  except ClientError as ex:     
    print(f'Error deploying Lambda Edge in us-east-1 with error: {ex}')  
    cfnResponse.send(event, context, cfnResponse.FAILED, {}, "LambdaEdgeCustomResourcePhysicalID")  
