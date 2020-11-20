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
Lambda function used as an AWS AppSync datasource to return an address based in the coordinates passed as parameter.
"""

import json
import uuid 
import os
import herepy

def handler(event, context):
    """
    Handler for the Lambda function.

    Gets the coordinates as input from the AWS AppSync API, then gets the address information using the Geocoder Reverse HERE API.
    """

    print('request: {}'.format(json.dumps(event)))
    latitude = float(event['arguments']['coordinates']['latitude'])
    longitude = float(event['arguments']['coordinates']['longitude'])

    here_api_key = os.environ['HERE_API_KEY']
    geocoder_reverse_api = herepy.GeocoderReverseApi(here_api_key)
    response_here = geocoder_reverse_api.retrieve_addresses([latitude,longitude])
    
    response_location = response_here.items[0]
    response_address = response_location['address'] 
    response_location = response_location['position']
    
    address = {
      'street': response_address['label'],
      'city': response_address['city'],
      'state': response_address['state'],
      'country': response_address['countryCode'],
      'latitude': response_location['lat'],
      'longitude': response_location['lng']
    }
  
    print('response: {}'.format(json.dumps(address)))    
    return address
