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

import React, { Component } from 'react';

import { ThemeProvider as MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';
import { blue } from '@material-ui/core/colors';

import { API, graphqlOperation } from 'aws-amplify';

import { listGeofences } from '../graphql/queries';

import GeofenceForm from "./GeofenceForm";
import GeofenceTable from "./GeofenceTable";

const theme = createMuiTheme({
  status: {
    danger: blue[500],
  },
});

class GeofenceHome extends Component {
  state = {
    data:[]
  };

  queryGeofences = async () => {
    console.log('queryGeofences')
    try {
      let allGeofences = await API.graphql(graphqlOperation(
        listGeofences
      ));        
      
      let items = await allGeofences.data.listGeofences.items;
      this.setState({ data: items });     
    } catch (err) {
      console.error('Err List Geofences => ' + JSON.stringify(err, null, 4))
    }
};

async componentDidMount() {
  await this.queryGeofences();
}

  render() {    
    return (
      <MuiThemeProvider theme={theme}>
        <div className="App">  
          <GeofenceForm queryGeofences = {this.queryGeofences} />
          <br/><br/>
          <GeofenceTable    
            queryGeofences = {this.queryGeofences}
            data = {this.state.data}
            header = {[
              {
                name: "Name",
                prop: "name"
              },
              {
                name: "Branch",
                prop: "branch"
              },
              {
                name: "City",
                prop: "city"
              }
            ]}
          />
          <br/><br/>
        </div>
      </MuiThemeProvider>
    );
  }

}

export default GeofenceHome;
