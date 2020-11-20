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
Lambda function used together with DynamoDB Streams to index data into Amazon ElasticSearch.
"""

import json
import os
import decimal

import boto3
from boto3.dynamodb.types import TypeDeserializer
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

region = os.environ['REGION']
host = os.environ['ES_HOST']

service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

def handler(event, context):
  """
  Main handler function that gets the data from the request and perform operations into Amazon ElasticSearch to create of update index. 
  """

  print('Request: {}'.format(json.dumps(event, indent = 4)))
  count = 0
  index_name = 'index-geofences'

  es = Elasticsearch(
    hosts = [{'host': host, 'port': 443}],
    http_auth = awsauth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection
  )

  print('Cluster Info: {}'.format(json.dumps(es.info(), indent = 4))) 

  for record in event['Records']:
    try:
      # to test if the indexed data was properly indexed
      # uncomment the line below and comment the if/else block
      #get_geofence(es, record, index_name)

      if record['eventName'] == 'INSERT' or record['eventName'] == 'MODIFY':
        index_geofence(es, record, index_name)  
      elif record['eventName'] == 'REMOVE':
        unindex_geofence(es, record, index_name)  

    except Exception as e:
      print("Failed to process:")
      print('Record: {}'.format(json.dumps(record, indent = 4)))
      print("ERROR: " + repr(e))
      continue  

    count += 1
  return f'{count} records processed.'
  
def index_geofence(es, record, index_name):
  """
  Index data into the Amazon ElstichSearch cluster
  """

  print('Indexing data into ES...')

  if es.indices.exists(index_name) == False:
    print(f'Index {index_name} not found. Creating it...')

    es.indices.create(
      index_name,
      body='{"settings": { "index.mapping.coerce": true } }')

    print(f'Index {index_name} created successfuly')

  else:
    print(f'Index {index_name} already exists...')

  geofence_to_index_id = get_id(record)
  print('geofence_to_index_id: {}'.format(geofence_to_index_id))

  geofence_to_index = convert_from_dbb_format_to_obj(record['dynamodb']['NewImage'])
  print('geofence_to_index: {}'.format(geofence_to_index))

  es.index(
    index = index_name,
    body = geofence_to_index,
    id = geofence_to_index_id,
    doc_type = index_name,
    refresh = True
  )
  print(f'Successly inserted geofence ID {geofence_to_index_id} to index {index_name}')

def unindex_geofence(es, record, index_name):
  """
  Removes indexed data from the Amazon ElstichSearch cluster
  """

  print('Removing indexed data from ES...')
  geofence_to_index_id = get_id(record)
  print('geofence_to_index_id: {}'.format(geofence_to_index_id))

  es.delete(
    index = index_name,
    id = geofence_to_index_id,
    doc_type = index_name,
    refresh = True
  )

  print(f'Successly removed geofence ID {geofence_to_index_id} to index {index_name}')

def get_geofence(es, record, index_name):
  """
  Gets the indexed data from the Amazon ElstichSearch cluster for testing purposes.
  """
  print('Getting data into ES for testing purposes...')
  geofence_to_index_id = get_id(record)
  print('geofence_to_index_id: {}'.format(geofence_to_index_id))

  response_geofence = es.get(
    index = index_name, 
    doc_type = index_name,
    id = geofence_to_index_id
  )

  print('response_geofence: {}'.format(json.dumps(response_geofence, indent = 4)))

def get_id(record):
  """
  Returns the Amazon DynamoDB key.
  """

  return record['dynamodb']['Keys']['id']['S']

def convert_from_dbb_format_to_obj(data):
  """
  Normalizes the object coming from Amazon DynamoDB in order to index a clean object in Amazon ElasticSearch.
  """

  return {k: normalize_values(TypeDeserializer().deserialize(v)) for k,v in data.items()}
  
def normalize_values(value):
  """
  Normalize values coming from Amazon DynamoDB.
  """

  if isinstance(value, decimal.Decimal):
    if value % 1 == 0:
      return int(value)
    else:
      return float(value)
  return value     
