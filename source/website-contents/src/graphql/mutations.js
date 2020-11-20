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

export const createGeofence = `mutation CreateGeofence($input: CreateGeofenceInput!) {
  createGeofence(input: $input) {
    id
    name
    branch
    address
    city
    country
    region
    latitude
    longitude
    definition
    visits
  }
} 
`;

export const updateGeofence = `mutation updateGeofence($input: UpdateGeofenceInput!) {
  updateGeofence(input: $input) {
    id
    name
    branch
    address
    city
    country
    region
    latitude
    longitude
    definition
    visits
  }
}
`;

export const deleteGeofence = `mutation deleteGeofence($input: DeleteGeofenceInput!) {
  deleteGeofence(input: $input) {
    id
  }
}
`;

export const createGeofenceMessage = `mutation createGeofenceMessage($template: String!, $input: GeofenceMessageInput!) {
  createGeofenceMessage(
    template: $template,
    input: $input
  ) {
    status
    message
  }
}
`;

export const deleteGeofenceMessage = `mutation deleteGeofenceMessage($template: String!) {
  deleteGeofenceMessage(
    template: $template
  ) {
    status
    message
  }
}
`;
