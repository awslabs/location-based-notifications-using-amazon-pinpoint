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

const AWS = require('aws-sdk');
const FormData = require('form-data');
const fs = require('fs');
const cfn_response = require('./cfn-response.js');

const region = process.env.REGION;
const domain = process.env.DOMAIN;

/**
 * 
 * Custom resource function to be invoked by the CloudFormation stack in oder to create the proper dashboards inside Kibana
 * 
 * This function loads a pre-defined ndjson file with a sample dashboard that it will ne deployed at the stack creating time.
 * This custom resource will be processed only for the Create event, otherwise it will move forward without any actios.
 */
exports.handler = async function (event, context) {
  console.log("Event:", event);
  const physicalId = "ESCustomResourceId";
  var requestSuccessful = true;
  const requests = event.ResourceProperties.Requests;
  const requestType = event.RequestType;

  if (requestType === 'Create') {
    await requests.reduce(async (previousPromise, request) => {
      return previousPromise
        .then(_result => { return sendDocument(request.method, request.path) })
        .then(handleSuccess);
    }, Promise.resolve())
      .catch(error => {
        console.error({ error });
        requestSuccessful = false;
      });

    if (event.ResponseURL) {
      console.log({requestSuccessful});
      const status = requestSuccessful ? cfn_response.SUCCESS : cfn_response.FAILED;
      await cfn_response.send(event, context, status, {}, physicalId);
    }
  } else {
    await cfn_response.send(event, context, cfn_response.SUCCESS, {}, physicalId);
  }
};

/**
 * 
 * Creates a request object to ElasticSearch passing the sample dashboards as body.
 */
function sendDocument(httpMethod, path) {
  return new Promise(function (resolve, reject) {
    var endpoint = new AWS.Endpoint(domain);
    var request = new AWS.HttpRequest(endpoint, region);

    var body = new FormData();
    body.append('file', fs.readFileSync('./kibana-objects.ndjson', 'utf8'), 'kibana-objects.ndjson')

    request.method = httpMethod;
    request.headers = body.getHeaders();
    request.headers['kbn-xsrf'] = 'kibana'
    request.headers['host'] = domain;
    request.path += path;
    console.log(body.getBuffer().toString('utf-8'))
    request.body =  body.getBuffer();

    var credentials = new AWS.EnvironmentCredentials('AWS');
    var signer = new AWS.Signers.V4(request, 'es');
    signer.addAuthorization(credentials, new Date());

    var client = new AWS.HttpClient();
    client.handleRequest(request, null, function (response) {
      var responseBody = '';
      response.on('data', function (chunk) {
        responseBody += chunk;
      });
      response.on('end', function (_chunk) {
        resolve({ "status": response.statusCode, "body": responseBody });
      });
    }, function (error) {
      console.error('Error: ' + error);
      reject(error);
    });
  });
}

/**
 * Validates if the request was successfull, it throws an exception otherwise.
 */
function handleSuccess(response) {
  if (response.status >= 200 && response.status < 300) {
    console.log("Successful request:", response);
  } else {
    throw new Error("Request failed: " + JSON.stringify(response)); 
  }
}
