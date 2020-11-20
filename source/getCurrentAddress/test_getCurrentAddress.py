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

import os
import json
import getCurrentAddress
from herepy.models import GeocoderReverseResponse

class TestGetCurrentAddress(unittest.TestCase):
  """
  Test class for the GetCurrentAddressLambda function 
  """

  ENV_HERE_API_KEY = 'HERE_API_KEY'
  HERE_API_KEY = 'some-sample-key'

  def setUp(self):
    """
    Setting up the test case
    """
    os.environ[TestGetCurrentAddress.ENV_HERE_API_KEY] = TestGetCurrentAddress.HERE_API_KEY
  
  @patch('herepy.GeocoderReverseApi')
  def test_get_current_address_successfully(self, mock_GeocoderReverseApi):
    """
    Test when getting the current address successfully
    """

    event = {
      'arguments': {
        'coordinates': {
          'latitude': -11.1234567,
          'longitude': -99.0987654
        }
      }
    }

    returned_address = {
      'items': [{
        'address': {
          'label': 'some_address',
          'city': 'some_city',
          'state': 'some_state',
          'countryCode': 'some_country_code'
        },
        'position': {
          'lat': -11.1234567,
          'lng': -99.0987654
        }
      }]
    }

    geocoderResponse = GeocoderReverseResponse().new_from_jsondict(returned_address)    
    mock_GeocoderReverseApi().retrieve_addresses.return_value = geocoderResponse
    
    returned_address = getCurrentAddress.handler(event, None)

    expected_address = {
      'street': 'some_address',
      'city': 'some_city',
      'state': 'some_state',
      'country': 'some_country_code',
      'latitude': -11.1234567,
      'longitude': -99.0987654
    } 

    self.assertTrue(returned_address)
    self.assertEqual(returned_address['street'], 'some_address')
    self.assertEqual(returned_address['city'], 'some_city')
    self.assertEqual(returned_address['state'], 'some_state')
    self.assertEqual(returned_address['country'], 'some_country_code')
    self.assertEqual(returned_address['latitude'], -11.1234567)
    self.assertEqual(returned_address['longitude'], -99.0987654)

if __name__ == '__main__':
    unittest.main()    
    